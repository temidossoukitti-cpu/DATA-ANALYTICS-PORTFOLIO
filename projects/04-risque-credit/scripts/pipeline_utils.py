"""Fonctions partagées du pipeline reproductible du projet 04."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_XLS = PROJECT_ROOT / "data" / "raw" / "default_of_credit_card_clients.xls"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"
VISUALS_DIR = PROJECT_ROOT / "visuals"
EXPECTED_RAW_SHA256 = "30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933"

RAW_RENAME = {
    "ID": "client_id",
    "LIMIT_BAL": "limit_bal",
    "SEX": "sex",
    "EDUCATION": "education",
    "MARRIAGE": "marriage",
    "AGE": "age",
    "PAY_0": "pay_0",
    "PAY_2": "pay_2",
    "PAY_3": "pay_3",
    "PAY_4": "pay_4",
    "PAY_5": "pay_5",
    "PAY_6": "pay_6",
    "BILL_AMT1": "bill_amt1",
    "BILL_AMT2": "bill_amt2",
    "BILL_AMT3": "bill_amt3",
    "BILL_AMT4": "bill_amt4",
    "BILL_AMT5": "bill_amt5",
    "BILL_AMT6": "bill_amt6",
    "PAY_AMT1": "pay_amt1",
    "PAY_AMT2": "pay_amt2",
    "PAY_AMT3": "pay_amt3",
    "PAY_AMT4": "pay_amt4",
    "PAY_AMT5": "pay_amt5",
    "PAY_AMT6": "pay_amt6",
    "default payment next month": "default_next_month",
}
SOURCE_COLUMN_ORDER = list(RAW_RENAME)
PAY_COLUMNS = ["pay_0", "pay_2", "pay_3", "pay_4", "pay_5", "pay_6"]
BILL_COLUMNS = [f"bill_amt{i}" for i in range(1, 7)]
PAY_AMOUNT_COLUMNS = [f"pay_amt{i}" for i in range(1, 7)]
AGE_BANDS = ["<25", "25-34", "35-44", "45-54", "55+"]
UTILIZATION_BANDS = ["<30 %", "30-<60 %", "60-100 %", ">100 %"]
RISK_BANDS = [
    (1, "Faible", 0.00, 0.10),
    (2, "Modéré", 0.10, 0.20),
    (3, "Élevé", 0.20, 0.40),
    (4, "Très élevé", 0.40, 1.00),
]


def read_raw_xls() -> pd.DataFrame:
    """Lit l’original UCI sans l’écrire; l’en-tête métier est sur la ligne 2."""
    frame = pd.read_excel(RAW_XLS, header=1, engine="xlrd")
    if list(frame.columns) != SOURCE_COLUMN_ORDER:
        raise ValueError("Les colonnes du XLS ne correspondent pas au schéma UCI attendu.")
    if frame.shape != (30_000, 25):
        raise ValueError(f"Dimensions inattendues pour le XLS : {frame.shape}.")
    frame = frame.rename(columns=RAW_RENAME)
    for column in frame.columns:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    return frame


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def default_rate(values: pd.Series) -> float:
    """Définition unique du taux de défaut pour tous les calculs Python."""
    return float(values.mean()) if len(values) else float("nan")


def engineer_features(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Recodages conservatifs et variables dérivées, sans suppression de clients."""
    frame = raw.copy()
    frame["education_original"] = frame["education"].astype("int64")
    frame["marriage_original"] = frame["marriage"].astype("int64")
    frame["education"] = frame["education_original"].replace({0: 4, 5: 4, 6: 4}).astype("int64")
    frame["marriage"] = frame["marriage_original"].replace({0: 3}).astype("int64")

    age_conditions = [
        frame["age"] < 25,
        frame["age"].between(25, 34),
        frame["age"].between(35, 44),
        frame["age"].between(45, 54),
        frame["age"] >= 55,
    ]
    frame["age_band"] = np.select(age_conditions, AGE_BANDS, default="Non classé")
    age_key = {label: index for index, label in enumerate(AGE_BANDS, start=1)}
    frame["age_band_key"] = frame["age_band"].map(age_key).astype("int64")

    band_codes = pd.qcut(frame["limit_bal"], q=5, labels=False, duplicates="drop")
    frame["limit_band_key"] = (band_codes.astype("int64") + 1)
    band_count = int(frame["limit_band_key"].max())
    limit_labels = {index: f"Q{index}" for index in range(1, band_count + 1)}
    frame["limit_band"] = frame["limit_band_key"].map(limit_labels)

    frame["education_key"] = frame["education"].astype("int64")
    frame["marriage_key"] = frame["marriage"].astype("int64")
    pay_values = sorted({int(value) for column in PAY_COLUMNS for value in frame[column].dropna().unique()})
    pay_key = {code: index for index, code in enumerate(pay_values, start=1)}
    frame["pay_status_key"] = frame["pay_0"].map(pay_key).astype("int64")

    limits = frame["limit_bal"].replace(0, np.nan)
    frame["utilization_raw"] = frame["bill_amt1"] / limits
    frame["utilization"] = frame["utilization_raw"].clip(lower=0.0, upper=1.5)
    frame["utilization_band"] = np.select(
        [
            frame["utilization"] < 0.30,
            frame["utilization"] < 0.60,
            frame["utilization"] <= 1.00,
            frame["utilization"] > 1.00,
        ],
        UTILIZATION_BANDS,
        default="Non classé",
    )
    frame["payment_ratio_m1"] = np.where(
        frame["bill_amt1"] > 0,
        frame["pay_amt1"] / frame["bill_amt1"].where(frame["bill_amt1"] > 0),
        np.nan,
    )
    pay_history = frame[PAY_COLUMNS]
    frame["max_delay_6m"] = pay_history.where(pay_history >= 1).max(axis=1).fillna(0).astype("int64")
    frame["n_delays_6m"] = (pay_history >= 1).sum(axis=1).astype("int64")
    frame["risk_flag_recent_delay"] = (frame["pay_0"] >= 1).astype("int64")

    frame["predicted_pd"] = np.nan
    frame["risk_band_key"] = np.nan
    frame["model_partition"] = "Non scoré"

    education_labels = {
        1: "Études supérieures",
        2: "Université",
        3: "Lycée",
        4: "Autre ou inconnu",
    }
    marriage_labels = {1: "Marié", 2: "Célibataire", 3: "Autre ou inconnu"}
    pay_labels = {
        -2: "Aucun achat déclaré (hypothèse)",
        -1: "Paiement à jour",
        0: "Crédit renouvelable (hypothèse)",
        **{value: f"Retard de {value} mois ou plus" if value == 9 else f"Retard de {value} mois" for value in range(1, 10)},
    }
    age_dimension = pd.DataFrame(
        [{"age_band_key": key, "age_band_label": label, "ordre": key} for key, label in enumerate(AGE_BANDS, start=1)]
    )
    education_dimension = pd.DataFrame(
        [{"education_key": code, "education_code": code, "education_label": label} for code, label in education_labels.items()]
    )
    marriage_dimension = pd.DataFrame(
        [{"marriage_key": code, "marriage_code": code, "marriage_label": label} for code, label in marriage_labels.items()]
    )
    pay_dimension = pd.DataFrame(
        [{"pay_status_key": pay_key[code], "pay_code": code, "pay_status_label": pay_labels.get(code, "Code non documenté")} for code in pay_values]
    ).sort_values("pay_status_key")
    limit_rows = []
    for key in range(1, band_count + 1):
        group = frame.loc[frame["limit_band_key"] == key, "limit_bal"]
        limit_rows.append(
            {
                "limit_band_key": key,
                "limit_band_label": limit_labels[key],
                "lower_limit": int(group.min()),
                "upper_limit": int(group.max()),
                "clients": int(group.size),
            }
        )
    limit_dimension = pd.DataFrame(limit_rows)
    risk_dimension = pd.DataFrame(
        [
            {
                "risk_band_key": key,
                "risk_band_label": label,
                "probability_min": minimum,
                "probability_max": maximum,
                "ordre": key,
            }
            for key, label, minimum, maximum in RISK_BANDS
        ]
    )
    dimensions = {
        "dim_age_band": age_dimension,
        "dim_education": education_dimension,
        "dim_marriage": marriage_dimension,
        "dim_limit_band": limit_dimension,
        "dim_pay_status": pay_dimension,
        "dim_risk_band": risk_dimension,
    }
    return frame, dimensions


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8", float_format="%.8f", na_rep="")
