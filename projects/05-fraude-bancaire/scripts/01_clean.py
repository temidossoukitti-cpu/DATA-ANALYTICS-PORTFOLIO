"""Contrôle l'échantillon versionné et construit les tables d'analyse Power BI."""
from __future__ import annotations

import numpy as np
import pandas as pd

from pipeline_utils import AMOUNT_BANDS, MODEL_FEATURES, RAW_COLS, ROOT, TIME_WINDOWS, add_bands, load_sample, population_values


def row(scope: str, rule: str, checked: int, exceptions: int, severity: str, status: str, action: str) -> dict:
    return {"scope": scope, "rule": rule, "rows_checked": int(checked), "exceptions": int(exceptions), "severity": severity, "status": status, "action": action}


def main() -> None:
    frame = load_sample()
    pop = population_values()
    n_source = int(float(pop["transactions_total"]))
    n_fraud = int(float(pop["transactions_fraud"]))
    n_legit = int(float(pop["transactions_legitimes"]))
    quality = []

    # Source checks were measured once by 00_make_sample.py on the full Parquet;
    # their counts are retained in population_kpis.csv for clean-clone runs.
    source_checks = [
        ("source_missing_cells", int(float(pop["missing_cells"])), "Aucune valeur manquante dans les colonnes source."),
        ("source_negative_amount_rows", int(float(pop["negative_amount_rows"])), "Amount ne doit pas être négatif."),
        ("source_negative_time_rows", int(float(pop["negative_time_rows"])), "Time ne doit pas être négatif."),
        ("source_label_conflict_groups", int(float(pop["feature_groups_with_label_conflict"])), "Un même profil source hors cible ne doit pas porter deux classes."),
    ]
    for rule, exceptions, action in source_checks:
        quality.append(row("full_source", rule, n_source, exceptions, "critique", "PASS" if exceptions == 0 else "FAIL", action))
    duplicate_source = int(float(pop["exact_duplicate_rows"]))
    quality.append(row("full_source", "source_exact_duplicate_rows", n_source, duplicate_source, "information", "INFO", "Lignes conservées telles quelles; les groupes identiques seront maintenus dans un même pli train/test."))
    fraud_excess = int(float(pop["exact_duplicate_fraud_rows"]))
    quality.append(row("full_source", "source_duplicate_fraud_rows", n_fraud, fraud_excess, "information", "INFO", "Toutes les lignes Class=1 sont conservées, y compris les répétitions exactes."))

    required = [*RAW_COLS, "transaction_id", "sampling_weight"]
    missing_columns = sum(column not in frame.columns for column in required)
    quality.append(row("committed_sample", "required_columns_present", len(required), missing_columns, "critique", "PASS" if missing_columns == 0 else "FAIL", "Schéma source, identifiant technique et poids d'échantillonnage présents."))
    n = len(frame)
    missing_cells = int(frame[RAW_COLS].isna().sum().sum())
    quality.append(row("committed_sample", "missing_cells", n * len(RAW_COLS), missing_cells, "critique", "PASS" if missing_cells == 0 else "FAIL", "Aucune imputation n'est pratiquée; toute valeur manquante bloque le pipeline."))
    finite = np.isfinite(frame[RAW_COLS].select_dtypes(include=[np.number]).to_numpy()).all(axis=1)
    nonfinite_rows = int((~finite).sum())
    quality.append(row("committed_sample", "nonfinite_numeric_rows", n, nonfinite_rows, "critique", "PASS" if nonfinite_rows == 0 else "FAIL", "Les colonnes numériques doivent être finies."))
    bad_target = int((~frame["Class"].isin([0, 1])).sum())
    quality.append(row("committed_sample", "target_outside_0_1", n, bad_target, "critique", "PASS" if bad_target == 0 else "FAIL", "Class doit être binaire : 0 légitime, 1 fraude."))
    negative_amount = int(frame["Amount"].lt(0).sum())
    quality.append(row("committed_sample", "negative_amount_rows", n, negative_amount, "critique", "PASS" if negative_amount == 0 else "FAIL", "Aucune valeur négative de Amount n'est attendue."))
    invalid_time = int((frame["Time"].lt(0) | frame["Time"].gt(float(pop["time_max_seconds"]))).sum())
    quality.append(row("committed_sample", "time_outside_source_range", n, invalid_time, "critique", "PASS" if invalid_time == 0 else "FAIL", "Time reste dans la plage observée du fichier source."))
    fraud_sample = int(frame["Class"].eq(1).sum())
    legit_sample = int(frame["Class"].eq(0).sum())
    fraud_design_ok = fraud_sample == n_fraud
    quality.append(row("committed_sample", "all_source_fraud_rows_retained", n_fraud, abs(n_fraud - fraud_sample), "critique", "PASS" if fraud_design_ok else "FAIL", "Recensement complet des fraudes, aucune ligne Class=1 retirée."))
    legitimate_weight_total = float(frame.loc[frame["Class"].eq(0), "sampling_weight"].sum())
    fraud_weight_total = float(frame.loc[frame["Class"].eq(1), "sampling_weight"].sum())
    weight_diff = int(round(abs((legitimate_weight_total + fraud_weight_total) - n_source)))
    quality.append(row("committed_sample", "design_weights_reconstruct_population", n, weight_diff, "critique", "PASS" if weight_diff == 0 else "FAIL", "Somme des poids d'inclusion égale à la population source."))
    duplicated = int(frame.duplicated(subset=RAW_COLS).sum())
    quality.append(row("committed_sample", "sample_exact_duplicate_rows", n, duplicated, "information", "INFO", "Répétitions conservées; elles sont groupées pour éviter une fuite entre partitions."))
    quality.append(row("committed_sample", "transaction_id_unique", n, int(frame["transaction_id"].duplicated().sum()), "critique", "PASS" if not frame["transaction_id"].duplicated().any() else "FAIL", "transaction_id représente uniquement le numéro de ligne source."))

    quality_frame = pd.DataFrame(quality)
    (ROOT / "results").mkdir(exist_ok=True)
    quality_frame.to_csv(ROOT / "results/quality_check.csv", index=False, encoding="utf-8")

    enriched = add_bands(frame)
    pd.DataFrame([{"outcome_key": 0, "label_fr": "Légitime", "is_fraud": 0}, {"outcome_key": 1, "label_fr": "Fraude", "is_fraud": 1}]).to_csv(ROOT / "data/processed/dim_outcome.csv", index=False, encoding="utf-8")
    pd.DataFrame(AMOUNT_BANDS).to_csv(ROOT / "data/processed/dim_amount_band.csv", index=False, encoding="utf-8")
    pd.DataFrame(TIME_WINDOWS).to_csv(ROOT / "data/processed/dim_time_window.csv", index=False, encoding="utf-8")
    fact = enriched[["transaction_id", "Time", "Amount", "outcome_key", "amount_band_key", "time_window_key", "sampling_weight"]].rename(columns={"Time": "time_seconds", "Amount": "amount"})
    fact.to_csv(ROOT / "data/processed/fact_transactions.csv", index=False, encoding="utf-8")

    fail_count = int(quality_frame["status"].eq("FAIL").sum())
    print(f"Contrôle/nettoyage : {n:,} lignes; {len(quality_frame)} règles comptées; {fail_count} échec(s); {fraud_sample:,} fraudes et {legit_sample:,} légitimes conservés.")
    print(f"Dimensions et fact_transactions.csv générés; doublons détectés et documentés : {duplicate_source:,} source, {duplicated:,} échantillon.")
    if fail_count:
        raise SystemExit("Contrôles qualité en échec; consulter results/quality_check.csv.")


if __name__ == "__main__":
    main()
