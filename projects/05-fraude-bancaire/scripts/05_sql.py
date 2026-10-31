"""Construit la base SQLite et vérifie la parité des métriques Python/SQL."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline_utils import ROOT


def run_query(connection: sqlite3.Connection, name: str) -> pd.DataFrame:
    sql = (ROOT / "sql" / name).read_text(encoding="utf-8")
    return pd.read_sql_query(sql, connection)


def main() -> None:
    processed = ROOT / "data/processed"
    database = processed / "fraud_controls.db"
    database.unlink(missing_ok=True)
    connection = sqlite3.connect(database)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript((ROOT / "sql/schema.sql").read_text(encoding="utf-8"))

    table_files = {
        "dim_outcome": processed / "dim_outcome.csv",
        "dim_amount_band": processed / "dim_amount_band.csv",
        "dim_time_window": processed / "dim_time_window.csv",
        "fact_transactions": processed / "fact_transactions.csv",
        "fact_model_test": processed / "fact_model_test.csv",
        "model_scorecard": processed / "model_scorecard.csv",
        "model_cost_sensitivity": processed / "model_cost_sensitivity.csv",
        "model_money_controls": processed / "model_money_controls.csv",
    }
    for table, path in table_files.items():
        frame = pd.read_csv(path)
        frame.to_sql(table, connection, if_exists="append", index=False)

    # Referential-integrity check before metric parity.
    foreign_key_errors = 0
    for table in ("fact_transactions", "fact_model_test"):
        foreign_key_errors += len(connection.execute(f"PRAGMA foreign_key_check({table})").fetchall())
    if foreign_key_errors:
        connection.close()
        raise SystemExit(f"Échec d'intégrité référentielle SQLite : {foreign_key_errors} ligne(s).")

    global_sql = run_query(connection, "01_global_fraud_rate.sql").iloc[0]
    amount_sql = run_query(connection, "02_fraud_by_amount_band.sql")
    time_sql = run_query(connection, "03_fraud_by_time_window.sql")
    model_sql = run_query(connection, "04_model_test_metrics.sql").iloc[0]
    money_sql = run_query(connection, "05_money_controls.sql").set_index("method")
    connection.close()

    overall = pd.read_csv(ROOT / "results/overall_kpis.csv").set_index("metric")["value"]
    amount_py = pd.read_csv(ROOT / "results/fraud_by_amount_band.csv").set_index("group_key")
    time_py = pd.read_csv(ROOT / "results/fraud_by_time_window.csv").set_index("group_key")
    model_py = pd.read_csv(ROOT / "results/model_metrics.csv").set_index("method")
    money_py = pd.read_csv(ROOT / "results/money_controls.csv").set_index("method")
    parity = []

    def compare(name: str, py_value: float, sql_value: float, tolerance: float) -> None:
        py_value, sql_value = float(py_value), float(sql_value)
        difference = abs(py_value - sql_value)
        parity.append({"indicator": name, "python_value": py_value, "sql_value": sql_value,
                       "absolute_difference": difference, "tolerance": tolerance,
                       "status": "PASS" if difference <= tolerance else "FAIL"})

    for metric, column, tolerance in [
        ("transactions_population_exact", "transactions_estimate", 0.01),
        ("fraud_transactions_population_exact", "fraud_transactions_estimate", 0.01),
        ("fraud_rate_weighted_sample", "fraud_rate", 1e-10),
        ("amount_total_weighted_sample", "amount_estimate", 0.01),
        ("fraud_amount_weighted_sample", "fraud_amount_estimate", 0.01),
    ]:
        compare(f"global.{metric}", overall.loc[metric], global_sql[column], tolerance)

    for key, row in amount_sql.set_index("amount_band_key").iterrows():
        py = amount_py.loc[key]
        for metric in ("transactions_estimate", "fraud_transactions_estimate", "fraud_rate", "amount_estimate", "fraud_amount_estimate"):
            tolerance = 1e-10 if metric == "fraud_rate" else 0.01
            compare(f"amount_band.{int(key)}.{metric}", py[metric], row[metric], tolerance)

    for key, row in time_sql.set_index("time_window_key").iterrows():
        py = time_py.loc[key]
        for metric in ("transactions_estimate", "fraud_transactions_estimate", "fraud_rate", "amount_estimate", "fraud_amount_estimate"):
            tolerance = 1e-10 if metric == "fraud_rate" else 0.01
            compare(f"time_window.{int(key)}.{metric}", py[metric], row[metric], tolerance)

    model = model_py.loc["Modèle logistique"]
    compare("model_test.precision_weighted", model["precision_weighted"], model_sql["precision_weighted"], 1e-10)
    compare("model_test.recall_weighted", model["recall_weighted"], model_sql["recall_weighted"], 1e-10)
    compare("model_test.transactions_estimate", model["test_transactions_population_estimate"], model_sql["transactions_estimate"], 0.01)

    for method, sql_row in money_sql.iterrows():
        py = money_py.loc[method]
        for metric in ("transactions_flagged_estimate", "fraud_transactions_intercepted_estimate",
                       "fraud_transactions_missed_estimate", "amount_flagged_estimate",
                       "fraud_amount_intercepted_estimate", "fraud_amount_missed_estimate",
                       "legitimate_amount_blocked_estimate", "expected_cost_estimate"):
            compare(f"money_controls.{method}.{metric}", py[metric], sql_row[metric], 0.02)

    parity_frame = pd.DataFrame(parity)
    parity_frame.to_csv(ROOT / "results/sql_parity.csv", index=False, encoding="utf-8")
    if (parity_frame["status"] != "PASS").any():
        failed = parity_frame.loc[parity_frame["status"] != "PASS", ["indicator", "python_value", "sql_value", "absolute_difference", "tolerance"]]
        print(failed.to_string(index=False))
        raise SystemExit("La parité Python/SQL contient des échecs; consulter results/sql_parity.csv.")
    print(f"SQLite recréée: {database.stat().st_size:,} octets; intégrité référentielle PASS.")
    print(f"Parité Python/SQL: {len(parity_frame)} indicateurs comparés, 0 échec(s).")


if __name__ == "__main__":
    main()
