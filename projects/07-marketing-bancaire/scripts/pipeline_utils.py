"""Fonctions communes au pipeline marketing, avec chemins relatifs au projet."""
from __future__ import annotations

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).parent.parent
RAW_PATH = ROOT / "data/raw/bank-additional-full.csv"
SEED = 42
TARGET = "y"
CATEGORICAL_FEATURES = [
    "job", "marital", "education", "default", "housing", "loan",
    "contact", "month", "day_of_week", "poutcome",
]
NUMERIC_FEATURES = [
    "age", "campaign", "pdays", "previous",
    "emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed",
]
MODEL_FEATURES = [*CATEGORICAL_FEATURES, *NUMERIC_FEATURES]
EXCLUDED_FEATURES = ["duration"]

MONTH_ORDER = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
MONTH_LABELS = {
    "jan": "Janvier", "feb": "Février", "mar": "Mars", "apr": "Avril",
    "may": "Mai", "jun": "Juin", "jul": "Juillet", "aug": "Août",
    "sep": "Septembre", "oct": "Octobre", "nov": "Novembre", "dec": "Décembre",
}
JOB_LABELS = {
    "admin.": "Administratif", "blue-collar": "Ouvrier", "entrepreneur": "Entrepreneur",
    "housemaid": "Aide à domicile", "management": "Cadre", "retired": "Retraité",
    "self-employed": "Indépendant", "services": "Services", "student": "Étudiant",
    "technician": "Technicien", "unemployed": "Sans emploi", "unknown": "Non renseigné",
}
EDUCATION_LABELS = {
    "illiterate": "Analphabète", "basic.4y": "Primaire (4 ans)",
    "basic.6y": "Primaire (6 ans)", "basic.9y": "Collège",
    "high.school": "Lycée", "professional.course": "Formation professionnelle",
    "university.degree": "Université", "unknown": "Non renseigné",
}
MARITAL_LABELS = {
    "divorced": "Divorcé ou veuf", "married": "Marié",
    "single": "Célibataire", "unknown": "Non renseigné",
}
CONTACT_LABELS = {"cellular": "Cellulaire", "telephone": "Téléphone"}
POUTCOME_LABELS = {
    "failure": "Échec", "nonexistent": "Inexistant", "success": "Succès",
}
AGE_BANDS = [
    {"age_band_key": 1, "label_fr": "17–25 ans", "lower_inclusive": 17, "upper_inclusive": 25, "sort_order": 1},
    {"age_band_key": 2, "label_fr": "26–35 ans", "lower_inclusive": 26, "upper_inclusive": 35, "sort_order": 2},
    {"age_band_key": 3, "label_fr": "36–45 ans", "lower_inclusive": 36, "upper_inclusive": 45, "sort_order": 3},
    {"age_band_key": 4, "label_fr": "46–55 ans", "lower_inclusive": 46, "upper_inclusive": 55, "sort_order": 4},
    {"age_band_key": 5, "label_fr": "56–65 ans", "lower_inclusive": 56, "upper_inclusive": 65, "sort_order": 5},
    {"age_band_key": 6, "label_fr": "66 ans et plus", "lower_inclusive": 66, "upper_inclusive": None, "sort_order": 6},
]
CAMPAIGN_BANDS = [
    {"campaign_band_key": 1, "label_fr": "1 contact", "lower_inclusive": 1, "upper_inclusive": 1, "sort_order": 1},
    {"campaign_band_key": 2, "label_fr": "2–3 contacts", "lower_inclusive": 2, "upper_inclusive": 3, "sort_order": 2},
    {"campaign_band_key": 3, "label_fr": "4–6 contacts", "lower_inclusive": 4, "upper_inclusive": 6, "sort_order": 3},
    {"campaign_band_key": 4, "label_fr": "7 contacts et plus", "lower_inclusive": 7, "upper_inclusive": None, "sort_order": 4},
]


def load_raw() -> pd.DataFrame:
    if not RAW_PATH.is_file():
        raise FileNotFoundError(f"Fichier source absent : {RAW_PATH}")
    frame = pd.read_csv(RAW_PATH, sep=";")
    required = [*MODEL_FEATURES, "duration", TARGET]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError("Colonnes source absentes : " + ", ".join(missing))
    return frame


def enrich(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out.insert(0, "campaign_id", np.arange(1, len(out) + 1, dtype=int))
    out["outcome_key"] = out[TARGET].map({"no": 0, "yes": 1}).astype(int)
    out["job_key"] = out["job"].map({name: i + 1 for i, name in enumerate(JOB_LABELS)}).astype(int)
    out["education_key"] = out["education"].map({name: i + 1 for i, name in enumerate(EDUCATION_LABELS)}).astype(int)
    out["marital_key"] = out["marital"].map({name: i + 1 for i, name in enumerate(MARITAL_LABELS)}).astype(int)
    out["contact_key"] = out["contact"].map({name: i + 1 for i, name in enumerate(CONTACT_LABELS)}).astype(int)
    out["poutcome_key"] = out["poutcome"].map({name: i + 1 for i, name in enumerate(POUTCOME_LABELS)}).astype(int)
    out["month_key"] = out["month"].map(MONTH_ORDER).astype(int)
    out["month_number"] = out["month_key"]
    out["age_band_key"] = np.select(
        [out["age"].le(25), out["age"].le(35), out["age"].le(45), out["age"].le(55), out["age"].le(65)],
        [1, 2, 3, 4, 5], default=6,
    ).astype(int)
    out["campaign_band_key"] = np.select(
        [out["campaign"].le(1), out["campaign"].le(3), out["campaign"].le(6)],
        [1, 2, 3], default=4,
    ).astype(int)
    out["previously_contacted"] = out["pdays"].ne(999).astype(int)
    out["default_status"] = out["default"]
    out["housing_loan"] = out["housing"]
    out["personal_loan"] = out["loan"]
    return out


def dimension_frames(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    job_counts = frame["job"].value_counts()
    return {
        "dim_outcome": pd.DataFrame([
            {"outcome_key": 0, "label_fr": "Non souscrit", "is_subscription": 0},
            {"outcome_key": 1, "label_fr": "Souscrit", "is_subscription": 1},
        ]),
        "dim_job": pd.DataFrame([
            {"job_key": i + 1, "code_source": name, "label_fr": label, "sort_order": i + 1, "source_rows": int(job_counts.get(name, 0))}
            for i, (name, label) in enumerate(JOB_LABELS.items())
        ]),
        "dim_education": pd.DataFrame([
            {"education_key": i + 1, "code_source": name, "label_fr": label, "sort_order": i + 1}
            for i, (name, label) in enumerate(EDUCATION_LABELS.items())
        ]),
        "dim_marital": pd.DataFrame([
            {"marital_key": i + 1, "code_source": name, "label_fr": label, "sort_order": i + 1}
            for i, (name, label) in enumerate(MARITAL_LABELS.items())
        ]),
        "dim_month": pd.DataFrame([
            {"month_key": order, "code_source": name, "label_fr": MONTH_LABELS[name], "sort_order": order}
            for name, order in MONTH_ORDER.items()
        ]).sort_values("month_key").reset_index(drop=True),
        "dim_contact": pd.DataFrame([
            {"contact_key": i + 1, "code_source": name, "label_fr": label, "sort_order": i + 1}
            for i, (name, label) in enumerate(CONTACT_LABELS.items())
        ]),
        "dim_poutcome": pd.DataFrame([
            {"poutcome_key": i + 1, "code_source": name, "label_fr": label, "sort_order": i + 1}
            for i, (name, label) in enumerate(POUTCOME_LABELS.items())
        ]),
        "dim_age_band": pd.DataFrame(AGE_BANDS),
        "dim_campaign_band": pd.DataFrame(CAMPAIGN_BANDS),
    }


def make_groups(frame: pd.DataFrame) -> np.ndarray:
    columns = [column for column in frame.columns if column not in {"campaign_id", TARGET, "outcome_key"}]
    return pd.util.hash_pandas_object(frame[columns], index=False).to_numpy(dtype="uint64")


def stratified_group_split(y: np.ndarray, groups: np.ndarray, test_fraction: float = 0.30, seed: int = SEED):
    y = np.asarray(y, dtype=int)
    groups = np.asarray(groups)
    if len(y) != len(groups) or len(np.unique(groups)) < 10:
        raise ValueError("Groupes insuffisants ou incompatibles pour le split.")
    splitter = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=seed)
    fold_id = np.full(len(y), -1, dtype=int)
    for fold, (_, valid_index) in enumerate(splitter.split(np.zeros(len(y)), y, groups)):
        fold_id[valid_index] = fold
    if (fold_id < 0).any():
        raise RuntimeError("Au moins une ligne n'a pas reçu de pli.")
    class_counts = {label: int((y == label).sum()) for label in (0, 1)}
    choices = []
    for folds in combinations(range(10), 3):
        test = np.isin(fold_id, folds)
        class_errors = sum(abs(float((y[test] == label).sum()) / class_counts[label] - test_fraction) for label in (0, 1))
        size_error = abs(float(test.mean()) - test_fraction)
        choices.append((class_errors * 2 + size_error, size_error, folds, test))
    _, _, selected_folds, test_mask = min(choices, key=lambda item: (item[0], item[1], item[2]))
    return np.flatnonzero(~test_mask), np.flatnonzero(test_mask), tuple(selected_folds)


def build_model() -> Pipeline:
    categorical_columns = [
        "job_key", "marital_key", "education_key", "default_status", "housing_loan", "personal_loan",
        "contact_key", "month_key", "day_of_week", "poutcome_key",
    ]
    numeric_columns = [
        "age", "campaign", "pdays", "previous",
        "emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed",
    ]
    preprocessing = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_columns),
        ("num", StandardScaler(), numeric_columns),
    ])
    return Pipeline([
        ("preprocess", preprocessing),
        ("model", LogisticRegression(C=1.0, solver="lbfgs", max_iter=3000, class_weight="balanced", random_state=SEED)),
    ])


def metrics_at_threshold(y: np.ndarray, probability: np.ndarray, threshold: float) -> dict:
    y = np.asarray(y, dtype=int)
    prediction = (np.asarray(probability, dtype=float) >= threshold).astype(int)
    true_positive = int(((y == 1) & (prediction == 1)).sum())
    false_positive = int(((y == 0) & (prediction == 1)).sum())
    false_negative = int(((y == 1) & (prediction == 0)).sum())
    true_negative = int(((y == 0) & (prediction == 0)).sum())
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (true_positive + true_negative) / len(y) if len(y) else 0.0
    return {
        "threshold": float(threshold), "true_positive": true_positive, "false_positive": false_positive,
        "false_negative": false_negative, "true_negative": true_negative,
        "flagged": int(prediction.sum()), "precision": precision, "recall": recall,
        "f1": f1, "accuracy": accuracy,
    }


def fr_num(value: float, digits: int = 0) -> str:
    return f"{float(value):,.{digits}f}".replace(",", " ").replace(".", ",")


def fr_pct(value: float, digits: int = 2) -> str:
    return f"{float(value) * 100:.{digits}f}".replace(".", ",") + " %"
