"""Fonctions communes au pipeline de fraude, avec chemins relatifs au projet."""
from __future__ import annotations

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).parent.parent
RAW_COLS = ["Time", *[f"V{i}" for i in range(1, 29)], "Amount", "Class"]
MODEL_FEATURES = [*[f"V{i}" for i in range(1, 29)], "Amount"]
SEED = 42
AMOUNT_BANDS = [
    {"amount_band_key": 1, "label_fr": "≤ 10", "lower_exclusive": None, "upper_inclusive": 10.0, "sort_order": 1},
    {"amount_band_key": 2, "label_fr": "(10, 50]", "lower_exclusive": 10.0, "upper_inclusive": 50.0, "sort_order": 2},
    {"amount_band_key": 3, "label_fr": "(50, 200]", "lower_exclusive": 50.0, "upper_inclusive": 200.0, "sort_order": 3},
    {"amount_band_key": 4, "label_fr": "> 200", "lower_exclusive": 200.0, "upper_inclusive": None, "sort_order": 4},
]
TIME_WINDOWS = [
    {"time_window_key": i + 1, "label_fr": f"T{i+1:02d} · {i*6}–{(i+1)*6} h", "start_second": i * 21600, "end_second_exclusive": (i + 1) * 21600, "sort_order": i + 1}
    for i in range(8)
]


def load_sample() -> pd.DataFrame:
    path = ROOT / "data/processed/transactions_sample.parquet"
    if not path.is_file():
        raise FileNotFoundError(f"Échantillon commité absent : {path}")
    frame = pd.read_parquet(path)
    frame["Class"] = frame["Class"].astype(int)
    frame["transaction_id"] = frame["transaction_id"].astype(int)
    frame["sampling_weight"] = frame["sampling_weight"].astype(float)
    return frame


def population_values() -> dict[str, str]:
    path = ROOT / "results/population_kpis.csv"
    if not path.is_file():
        raise FileNotFoundError("results/population_kpis.csv absent; exécuter scripts/00_make_sample.py avec le Parquet complet.")
    frame = pd.read_csv(path, dtype={"value": str})
    return dict(zip(frame["metric"], frame["value"]))


def population_number(key: str) -> float:
    return float(population_values()[key])


def add_bands(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    amount = out["Amount"].astype(float)
    out["amount_band_key"] = np.select([amount.le(10), amount.le(50), amount.le(200)], [1, 2, 3], default=4).astype(int)
    out["time_window_key"] = np.minimum((out["Time"].astype(float) // 21600).astype(int) + 1, 8)
    out["outcome_key"] = out["Class"].astype(int)
    return out


def make_duplicate_groups(frame: pd.DataFrame) -> np.ndarray:
    columns = [c for c in RAW_COLS if c != "Class"]
    return pd.util.hash_pandas_object(frame[columns], index=False).to_numpy(dtype="uint64")


def calibrate_population_weights(y: np.ndarray, design_weights: np.ndarray) -> np.ndarray:
    """Post-stratifie les poids d'une partition sur les effectifs source connus."""
    y = np.asarray(y, dtype=int)
    out = np.asarray(design_weights, dtype=float).copy()
    totals = {0: population_number("transactions_legitimes"), 1: population_number("transactions_fraud")}
    for label, target_total in totals.items():
        mask = y == label
        if not mask.any() or out[mask].sum() <= 0:
            raise ValueError(f"La partition ne contient pas d'observations de classe {label}.")
        out[mask] *= target_total / out[mask].sum()
    return out


def weighted_quantile(values, quantile: float, weights) -> float:
    x = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    if not 0 <= quantile <= 1 or len(x) == 0 or len(x) != len(w) or np.any(w < 0) or w.sum() <= 0:
        raise ValueError("Valeurs/poids invalides pour le quantile pondéré.")
    order = np.argsort(x, kind="stable")
    x_sorted, w_sorted = x[order], w[order]
    index = min(np.searchsorted(np.cumsum(w_sorted), quantile * w_sorted.sum(), side="left"), len(x_sorted) - 1)
    return float(x_sorted[index])


def stratified_group_split(y: np.ndarray, groups: np.ndarray, test_fraction: float = 0.30, seed: int = SEED):
    """Split stratifié 70/30 approximatif; lignes identiques restent dans un même pli."""
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
    train_index = np.flatnonzero(~test_mask)
    test_index = np.flatnonzero(test_mask)
    return train_index, test_index, tuple(selected_folds)


def new_logistic_pipeline():
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(C=1.0, solver="lbfgs", max_iter=2000, random_state=SEED),
    )


def weighted_cost(y, predicted, amount, evaluation_weights, loss_severity: float, friction_cost: float) -> float:
    y = np.asarray(y, dtype=int)
    predicted = np.asarray(predicted, dtype=int)
    amount = np.asarray(amount, dtype=float)
    weights = np.asarray(evaluation_weights, dtype=float)
    missed = (y == 1) & (predicted == 0)
    false_positive = (y == 0) & (predicted == 1)
    return float(np.sum(weights[missed] * amount[missed] * loss_severity) + np.sum(weights[false_positive] * friction_cost))
