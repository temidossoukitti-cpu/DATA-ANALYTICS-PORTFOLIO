"""Prépare la table auxiliaire Power BI à partir des métriques calculées."""
from __future__ import annotations

import pandas as pd

from pipeline_utils import PROCESSED_DIR, RESULTS_DIR, write_csv


def main() -> None:
    metrics = pd.read_csv(RESULTS_DIR / "model_metrics.csv")
    if len(metrics) != 1:
        raise ValueError("La scorecard doit contenir exactement une ligne de résultats test.")
    metrics.insert(0, "scorecard_key", 1)
    write_csv(metrics, PROCESSED_DIR / "model_scorecard.csv")
    print("Table auxiliaire model_scorecard créée depuis results/model_metrics.csv.")


if __name__ == "__main__":
    main()
