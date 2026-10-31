"""Nettoie l’original UCI, trace les contrôles et exporte le schéma en étoile."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from pipeline_utils import (
    EXPECTED_RAW_SHA256,
    PAY_COLUMNS,
    RAW_XLS,
    PROCESSED_DIR,
    RESULTS_DIR,
    SOURCE_COLUMN_ORDER,
    engineer_features,
    read_raw_xls,
    sha256_file,
    write_csv,
)


def quality_row(rule: str, description: str, before: int | float, after: int | float, affected: int | float, status: str, note: str) -> dict:
    return {
        "rule": rule,
        "description": description,
        "count_before": before,
        "count_after": after,
        "affected_rows": affected,
        "status": status,
        "note": note,
    }


def build_quality_report(raw: pd.DataFrame, clean: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    source_hash = sha256_file(RAW_XLS)
    rows.append(quality_row("source_rows", "Nombre de clients lus dans le XLS", len(raw), len(clean), len(raw) - len(clean), "PASS" if len(raw) == len(clean) == 30_000 else "FAIL", "Aucune ligne n’est supprimée."))
    rows.append(quality_row("source_columns", "Colonnes UCI reconnues", len(raw.columns), len(clean.columns), abs(len(raw.columns) - 25), "PASS" if len(raw.columns) == 25 else "FAIL", "25 colonnes brutes; les champs dérivés sont ajoutés après lecture."))
    missing_before = int(raw.isna().sum().sum())
    rows.append(quality_row("missing_raw_values", "Valeurs manquantes dans les données brutes", missing_before, missing_before, missing_before, "PASS" if missing_before == 0 else "FAIL", "Aucune imputation n’est appliquée au fichier brut."))
    id_duplicates = int(raw["client_id"].duplicated(keep="first").sum())
    rows.append(quality_row("unique_client_id", "Unicité de l’identifiant client", len(raw), raw["client_id"].nunique(), id_duplicates, "PASS" if id_duplicates == 0 else "FAIL", "La clé client sert uniquement à la jointure; elle n’entre pas dans le modèle."))
    non_id = raw.drop(columns=["client_id"])
    duplicate_rows = int(non_id.duplicated(keep=False).sum())
    rows.append(quality_row("duplicate_profiles_excluding_id", "Profils dupliqués sur toutes les colonnes hors ID", len(raw), len(raw), duplicate_rows, "PASS", "Le contrôle est compté; les clients ne sont pas supprimés."))
    age_outside = int((~raw["age"].between(18, 100)).sum())
    rows.append(quality_row("age_range", "Âge hors de l’intervalle de contrôle 18–100", len(raw), len(raw) - age_outside, age_outside, "PASS" if age_outside == 0 else "FAIL", "Intervalle de contrôle analytique; aucune valeur n’est tronquée."))
    limit_invalid = int((raw["limit_bal"] <= 0).sum())
    rows.append(quality_row("positive_limit", "Limite de crédit non positive", len(raw), len(raw) - limit_invalid, limit_invalid, "PASS" if limit_invalid == 0 else "FAIL", "La division d’utilisation exige une limite positive."))
    sex_invalid = int((~raw["sex"].isin([1, 2])).sum())
    rows.append(quality_row("sex_codes", "Codes de sexe hors {1, 2}", len(raw), len(raw) - sex_invalid, sex_invalid, "PASS" if sex_invalid == 0 else "FAIL", "Champ conservé à des fins descriptives uniquement."))
    education_recode = int(raw["education"].isin([0, 5, 6]).sum())
    education_after = int(clean["education_original"].isin([0, 5, 6]).sum())
    rows.append(quality_row("education_unknown_codes", "Codes éducation 0, 5, 6 recodés vers 4", education_recode, education_after, education_recode, "PASS" if education_recode == education_after else "FAIL", "Valeur source conservée dans education_original; recodage documenté comme demandé."))
    marriage_recode = int((raw["marriage"] == 0).sum())
    marriage_after = int((clean["marriage_original"] == 0).sum())
    rows.append(quality_row("marriage_zero", "Code matrimonial 0 recodé vers 3", marriage_recode, marriage_after, marriage_recode, "PASS" if marriage_recode == marriage_after else "FAIL", "Valeur source conservée dans marriage_original."))
    pay_invalid = int(sum((~raw[column].between(-2, 9)).sum() for column in PAY_COLUMNS))
    rows.append(quality_row("payment_status_range", "Statuts de paiement hors [-2, 9]", len(raw) * len(PAY_COLUMNS), len(raw) * len(PAY_COLUMNS) - pay_invalid, pay_invalid, "PASS" if pay_invalid == 0 else "FAIL", "Les codes -2 et 0 sont des hypothèses métier explicitées dans DATA_DICTIONARY.md."))
    target_invalid = int((~raw["default_next_month"].isin([0, 1])).sum())
    rows.append(quality_row("binary_target", "Cible hors {0, 1}", len(raw), len(raw) - target_invalid, target_invalid, "PASS" if target_invalid == 0 else "FAIL", "1 représente un défaut le mois suivant."))
    raw_util = clean["utilization_raw"]
    low_clip = int((raw_util < 0).sum())
    high_clip = int((raw_util > 1.5).sum())
    rows.append(quality_row("utilization_negative_cap", "Utilisations négatives ramenées à zéro", low_clip, int((clean["utilization"] == 0).sum()), low_clip, "PASS", "Hypothèse documentée; les montants source restent inchangés."))
    rows.append(quality_row("utilization_upper_cap", "Utilisations supérieures à 150 % plafonnées", high_clip, int((clean["utilization"] == 1.5).sum()), high_clip, "PASS", "Hypothèse documentée; le ratio brut reste disponible pour audit."))
    ratio_missing = int(clean["payment_ratio_m1"].isna().sum())
    nonpositive_bill = int((clean["bill_amt1"] <= 0).sum())
    rows.append(quality_row("payment_ratio_denominator", "Ratio de paiement manquant lorsque le relevé n’est pas positif", nonpositive_bill, ratio_missing, ratio_missing, "PASS" if ratio_missing == nonpositive_bill else "FAIL", "Le ratio n’est calculé que lorsque bill_amt1 > 0."))
    rows.append(quality_row("source_sha256", "Empreinte du XLS brut conforme à SOURCE.md", 1, int(source_hash == EXPECTED_RAW_SHA256), int(source_hash != EXPECTED_RAW_SHA256), "PASS" if source_hash == EXPECTED_RAW_SHA256 else "FAIL", source_hash))
    return pd.DataFrame(rows)


def main() -> None:
    raw = read_raw_xls()
    clean, dimensions = engineer_features(raw)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(clean, PROCESSED_DIR / "fact_clients.csv")
    for name, dimension in dimensions.items():
        write_csv(dimension, PROCESSED_DIR / f"{name}.csv")
    quality = build_quality_report(raw, clean)
    write_csv(quality, RESULTS_DIR / "quality_check.csv")
    if (quality["status"] == "FAIL").any():
        failed = quality.loc[quality["status"] == "FAIL", "rule"].tolist()
        raise RuntimeError(f"Échec des contrôles qualité : {failed}")
    print(f"Nettoyage terminé : {len(clean)} clients; {len(SOURCE_COLUMN_ORDER)} colonnes source; {len(dimensions) + 1} tables Power BI.")


if __name__ == "__main__":
    main()
