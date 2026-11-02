"""Reconstruit SQLite et compare des KPI SQL aux sorties Python."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from pipeline_utils import ROOT


def main() -> None:
    processed = ROOT / "data/processed"
    db_path = processed / "bank_marketing.db"
    fact = pd.read_csv(processed / "fact_campaign.csv")
    with sqlite3.connect(db_path) as conn:
        fact.to_sql("fact_campaign", conn, if_exists="replace", index=False)
        checks = []
        sql_global = pd.read_sql_query(
            "SELECT COUNT(*) AS campaigns, SUM(outcome_key) AS subscriptions, "
            "CAST(SUM(outcome_key) AS REAL) / COUNT(*) AS conversion_rate "
            "FROM fact_campaign", conn,
        ).iloc[0]
        checks.extend([
            ("campaign_rows", float(sql_global.campaigns), float(len(fact))),
            ("subscriptions", float(sql_global.subscriptions), float(fact.outcome_key.sum())),
            ("conversion_rate", float(sql_global.conversion_rate), float(fact.outcome_key.mean())),
        ])
        sql_month = pd.read_sql_query(
            "SELECT month_key, COUNT(*) AS rows, SUM(outcome_key) AS subscriptions "
            "FROM fact_campaign GROUP BY month_key ORDER BY month_key", conn,
        )
        py_month = fact.groupby("month_key").agg(rows=("campaign_id", "count"), subscriptions=("outcome_key", "sum")).reset_index()
        checks.append(("month_aggregates", float((sql_month.equals(py_month))), 1.0))
        sql_job = pd.read_sql_query(
            "SELECT job_key, COUNT(*) AS rows, SUM(outcome_key) AS subscriptions "
            "FROM fact_campaign GROUP BY job_key ORDER BY job_key", conn,
        )
        py_job = fact.groupby("job_key").agg(rows=("campaign_id", "count"), subscriptions=("outcome_key", "sum")).reset_index()
        checks.append(("job_aggregates", float((sql_job.equals(py_job))), 1.0))
    parity = pd.DataFrame([
        {"check": name, "sql_value": sql_value, "python_value": python_value,
         "status": "PASS" if abs(sql_value - python_value) < 1e-9 else "FAIL"}
        for name, sql_value, python_value in checks
    ])
    parity.to_csv(ROOT / "results/sql_parity.csv", index=False, encoding="utf-8")
    if (parity.status == "FAIL").any():
        raise SystemExit("Parité SQL/Python en échec.")
    print(f"Parité SQL/Python : {len(parity)} contrôles PASS; base {db_path.name} générée.")


if __name__ == "__main__":
    main()
