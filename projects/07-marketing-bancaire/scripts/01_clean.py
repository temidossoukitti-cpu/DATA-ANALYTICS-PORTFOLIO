"""Contrôle la source marketing et construit le modèle en étoile Power BI."""
from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

from pipeline_utils import (
    AGE_BANDS, CAMPAIGN_BANDS, ROOT, dimension_frames, enrich, load_raw,
)


def row(scope: str, rule: str, checked: int, exceptions: int, severity: str, status: str, action: str) -> dict:
    return {"scope": scope, "rule": rule, "rows_checked": int(checked), "exceptions": int(exceptions), "severity": severity, "status": status, "action": action}


def main() -> None:
    raw = load_raw()
    n = len(raw)
    quality = []

    def record(rule: str, exceptions: int, action: str, severity: str = "critique", status: str | None = None) -> None:
        quality.append(row("source", rule, n, exceptions, severity, status or ("PASS" if exceptions == 0 else "FAIL"), action))

    required = {
        "age", "job", "marital", "education", "default", "housing", "loan", "contact",
        "month", "day_of_week", "duration", "campaign", "pdays", "previous", "poutcome",
        "emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed", "y",
    }
    record("required_columns_present", len(required.difference(raw.columns)), "Les 20 variables et la cible doivent être présentes.")
    record("missing_cells", int(raw.isna().sum().sum()), "Aucune valeur manquante explicite; les absences sont codées unknown.")
    duplicated = int(raw.duplicated().sum())
    quality.append(row("source", "exact_duplicate_rows", n, duplicated, "information", "INFO", "Doublons exacts conservés et regroupés pour empêcher une fuite entre train et test."))
    record("target_outside_no_yes", int((~raw["y"].isin(["no", "yes"])).sum()), "La cible doit valoir no ou yes.")
    record("age_outside_17_100", int((raw["age"].lt(17) | raw["age"].gt(100)).sum()), "L'âge doit rester dans une plage plausible.")
    record("duration_negative", int(raw["duration"].lt(0).sum()), "La durée d'appel ne peut pas être négative.")
    zero_yes = int((raw["duration"].eq(0) & raw["y"].eq("yes")).sum())
    record("duration_zero_with_subscription", zero_yes, "Une durée nulle ne doit jamais produire une souscription.")
    record("campaign_below_one", int(raw["campaign"].lt(1).sum()), "Chaque ligne compte au moins un contact de campagne.")
    record("pdays_outside_0_999", int((raw["pdays"].lt(0) | raw["pdays"].gt(999)).sum()), "pdays vaut 999 lorsque le client n'a jamais été contacté.")
    record("previous_negative", int(raw["previous"].lt(0).sum()), "Le nombre de contacts antérieurs ne peut pas être négatif.")
    record("month_unknown", int((~raw["month"].isin(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])).sum()), "Le mois doit être un code valide.")
    record("day_of_week_unknown", int((~raw["day_of_week"].isin(["mon", "tue", "wed", "thu", "fri"])).sum()), "Le jour doit être un jour ouvré valide.")
    economic_ranges = {
        "emp.var.rate": (-4.0, 2.0), "cons.price.idx": (92.0, 95.0), "cons.conf.idx": (-52.0, -25.0),
        "euribor3m": (0.5, 5.1), "nr.employed": (4900.0, 5300.0),
    }
    outside_economic = sum(int((raw[column].lt(low) | raw[column].gt(high)).sum()) for column, (low, high) in economic_ranges.items())
    record("economic_indicator_range", outside_economic, "Les cinq indicateurs macroéconomiques restent dans les plages documentées par la source.")
    unknown_rows = int(raw[[column for column in ("job", "marital", "education", "default", "housing", "loan")]].eq("unknown").any(axis=1).sum())
    quality.append(row("source", "rows_with_unknown_category", n, unknown_rows, "information", "INFO", "La modalité unknown est conservée comme catégorie explicite, sans imputation."))

    quality_frame = pd.DataFrame(quality)
    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    quality_frame.to_csv(results / "quality_check.csv", index=False, encoding="utf-8")

    sha256 = hashlib.sha256((ROOT / "data/raw/bank-additional-full.csv").read_bytes()).hexdigest()
    pd.DataFrame([{
        "source": "UCI Bank Marketing",
        "file": "bank-additional-full.csv",
        "sha256": sha256,
        "size_bytes": (ROOT / "data/raw/bank-additional-full.csv").stat().st_size,
        "rows": n,
        "columns": len(raw.columns),
    }]).to_csv(results / "source_integrity.csv", index=False, encoding="utf-8")

    enriched = enrich(raw)
    processed = ROOT / "data/processed"
    processed.mkdir(parents=True, exist_ok=True)
    dims = dimension_frames(enriched)
    for name, frame in dims.items():
        frame.to_csv(processed / f"{name}.csv", index=False, encoding="utf-8")

    age_lookup = {item["age_band_key"]: item["label_fr"] for item in AGE_BANDS}
    campaign_lookup = {item["campaign_band_key"]: item["label_fr"] for item in CAMPAIGN_BANDS}
    if enriched["age_band_key"].isna().any() or enriched["campaign_band_key"].isna().any():
        raise SystemExit("Bandes d'âge ou de campagne manquantes.")
    if not set(enriched["age_band_key"]).issubset(age_lookup) or not set(enriched["campaign_band_key"]).issubset(campaign_lookup):
        raise SystemExit("Clés de bande hors référentiel.")

    fact = enriched[[
        "campaign_id", "age", "age_band_key", "job_key", "marital_key", "education_key",
        "default_status", "housing_loan", "personal_loan", "contact_key", "month_key", "day_of_week",
        "duration", "campaign", "campaign_band_key", "pdays", "previously_contacted", "previous",
        "poutcome_key", "emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed",
        "outcome_key",
    ]]
    fact.to_csv(processed / "fact_campaign.csv", index=False, encoding="utf-8")

    fail_count = int(quality_frame["status"].eq("FAIL").sum())
    print(f"Contrôle/nettoyage : {n:,} lignes; {len(quality_frame)} règles; {fail_count} échec(s); {int(enriched['outcome_key'].sum()):,} souscriptions.")
    print(f"Dimensions {len(dims)} et fact_campaign.csv générés; doublons exacts : {duplicated:,}.")
    if fail_count:
        raise SystemExit("Contrôles qualité en échec; consulter results/quality_check.csv.")


if __name__ == "__main__":
    main()