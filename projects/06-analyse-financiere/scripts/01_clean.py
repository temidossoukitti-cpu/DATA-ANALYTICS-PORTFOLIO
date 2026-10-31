"""Extrait les états financiers SEC, contrôle la cohérence et construit l'étoile Power BI."""
from __future__ import annotations

import numpy as np
import pandas as pd

from pipeline_utils import (
    FY_END, FY_START, METRICS, RATIOS, ROOT, build_facts, compute_ratios,
    facts_to_metrics_matrix, load_companyfacts,
)


def row(scope: str, rule: str, checked: int, exceptions: int, severity: str, status: str, action: str) -> dict:
    return {"scope": scope, "rule": rule, "rows_checked": int(checked), "exceptions": int(exceptions),
            "severity": severity, "status": status, "action": action}


def main() -> None:
    quality = []
    facts_dict = load_companyfacts()
    entity = facts_dict.get("entityName", "")
    cik = int(facts_dict.get("cik", 0))
    quality.append(row("source", "entity_is_mastercard", 1, 0 if "Mastercard" in entity else 1,
                       "critique", "PASS" if "Mastercard" in entity else "FAIL",
                       f"Entité lue : {entity}."))
    quality.append(row("source", "cik_equals_1141391", 1, 0 if cik == 1141391 else 1,
                       "critique", "PASS" if cik == 1141391 else "FAIL",
                       "Identifiant SEC attendu de Mastercard Incorporated."))

    facts = build_facts()
    n_metrics = len(METRICS)
    n_years = FY_END - FY_START + 1
    quality.append(row("extraction", "metric_year_grid_complete", n_metrics * n_years,
                       n_metrics * n_years - len(facts), "critique",
                       "PASS" if len(facts) == n_metrics * n_years else "FAIL",
                       "Une valeur annuelle par indicateur et par exercice."))

    duplicated = int(facts.duplicated(subset=["fiscal_year", "metric_key"]).sum())
    quality.append(row("extraction", "duplicate_metric_year", len(facts), duplicated, "critique",
                       "PASS" if duplicated == 0 else "FAIL", "Clé (exercice, indicateur) unique."))

    nonfinite = int((~np.isfinite(facts["value"])).sum())
    quality.append(row("extraction", "nonfinite_values", len(facts), nonfinite, "critique",
                       "PASS" if nonfinite == 0 else "FAIL", "Toutes les valeurs sont finies."))

    matrix = facts_to_metrics_matrix(facts)
    negative_revenue = int((matrix["revenue"] <= 0).sum())
    quality.append(row("coherence", "positive_revenue", n_years, negative_revenue, "critique",
                       "PASS" if negative_revenue == 0 else "FAIL", "Les produits doivent être positifs."))
    negative_assets = int((matrix["total_assets"] <= 0).sum())
    quality.append(row("coherence", "positive_assets", n_years, negative_assets, "critique",
                       "PASS" if negative_assets == 0 else "FAIL", "Le total de l'actif doit être positif."))
    negative_equity = int((matrix["equity"] <= 0).sum())
    quality.append(row("coherence", "positive_equity", n_years, negative_equity, "critique",
                       "PASS" if negative_equity == 0 else "FAIL", "Les capitaux propres doivent rester positifs."))
    current_gt_total = int((matrix["current_assets"] > matrix["total_assets"]).sum()
                           + (matrix["current_liabilities"] > matrix["total_liabilities"]).sum())
    quality.append(row("coherence", "current_below_total", n_years * 2, current_gt_total, "critique",
                       "PASS" if current_gt_total == 0 else "FAIL",
                       "L'actif et le passif courants ne peuvent dépasser leurs totaux."))
    positive_interest = int((matrix["interest_expense"] <= 0).sum())
    quality.append(row("coherence", "positive_interest_expense", n_years, positive_interest, "critique",
                       "PASS" if positive_interest == 0 else "FAIL", "La charge d'intérêts sert de dénominateur."))

    balance_diff = (matrix["total_assets"] - (matrix["total_liabilities"] + matrix["equity"])).abs()
    balance_tolerance = matrix["total_assets"].abs() * 0.005
    balance_fail = int((balance_diff > balance_tolerance).sum())
    quality.append(row("coherence", "balance_sheet_identity", n_years, balance_fail, "information",
                       "INFO" if balance_fail == 0 else "FAIL",
                       "Écart actif = passif + capitaux propres toléré à 0,5 % du total de l'actif; "
                       "un écart résiduel relève d'intérêts minoritaires non détaillés."))

    implied_eps = matrix["net_income"] / matrix["diluted_shares"]
    eps_gap = (implied_eps - matrix["eps_diluted"]).abs() / matrix["eps_diluted"].abs()
    eps_fail = int((eps_gap > 0.01).sum())
    quality.append(row("coherence", "eps_matches_net_income", n_years, eps_fail, "critique",
                       "PASS" if eps_fail == 0 else "FAIL",
                       "BPA déclaré comparé à résultat net / actions diluées, tolérance 1 %."))

    ratios = compute_ratios(matrix)
    ratios_long = (ratios.reset_index().melt(id_vars="fiscal_year", var_name="ratio_key", value_name="value")
                   .dropna(subset=["value"]))
    ratio_missing = len(ratios.columns) * n_years - len(ratios_long)
    expected_missing = 3
    quality.append(row("ratios", "ratio_grid_complete", len(ratios.columns) * n_years,
                       ratio_missing - expected_missing, "critique",
                       "PASS" if ratio_missing == expected_missing else "FAIL",
                       f"Attendu : {expected_missing} valeurs manquantes (première année sans variation)."))

    quality_frame = pd.DataFrame(quality)
    (ROOT / "results").mkdir(exist_ok=True)
    quality_frame.to_csv(ROOT / "results/quality_check.csv", index=False, encoding="utf-8")

    processed = ROOT / "data/processed"
    processed.mkdir(parents=True, exist_ok=True)

    pd.DataFrame([
        {"fiscal_year": year, "period_end": f"{year}-12-31", "label_fr": f"Exercice {year}", "sort_order": year - FY_START + 1}
        for year in range(FY_START, FY_END + 1)
    ]).to_csv(processed / "dim_fiscal_year.csv", index=False, encoding="utf-8")

    pd.DataFrame([
        {"metric_key": m["metric_key"], "label_fr": m["label_fr"], "statement": m["statement"],
         "unit": m["unit"], "definition": m["definition"], "sort_order": m["sort_order"]}
        for m in METRICS
    ]).to_csv(processed / "dim_metric.csv", index=False, encoding="utf-8")

    pd.DataFrame([
        {"ratio_key": r["ratio_key"], "label_fr": r["label_fr"], "category": r["category"],
         "unit": r["unit"], "definition": r["definition"], "formula": r["formula"], "sort_order": r["sort_order"]}
        for r in RATIOS
    ]).to_csv(processed / "dim_ratio.csv", index=False, encoding="utf-8")

    facts.rename(columns={"fiscal_year": "fiscal_year_key"}).to_csv(
        processed / "fact_financials.csv", index=False, encoding="utf-8")
    ratios_long.rename(columns={"fiscal_year": "fiscal_year_key"}).to_csv(
        processed / "fact_ratios.csv", index=False, encoding="utf-8", float_format="%.10f")

    fail_count = int(quality_frame["status"].eq("FAIL").sum())
    print(f"Extraction : {n_metrics} indicateurs, {n_years} exercices ({FY_START}-{FY_END}); "
          f"{len(facts)} valeurs, {len(ratios.columns)} ratios; {fail_count} échec(s).")
    print(f"Écart bilan maximal : {balance_diff.max():,.0f} USD; écart BPA maximal : {eps_gap.max():.4%}.")
    if fail_count:
        raise SystemExit("Contrôles qualité en échec; consulter results/quality_check.csv.")


if __name__ == "__main__":
    main()
