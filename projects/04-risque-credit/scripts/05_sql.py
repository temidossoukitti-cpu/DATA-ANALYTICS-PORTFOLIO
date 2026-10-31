"""Reconstruit SQLite depuis les CSV traités et compare cinq familles d’indicateurs."""
from __future__ import annotations

import math
import sqlite3

import pandas as pd

from pipeline_utils import PROJECT_ROOT, PROCESSED_DIR, RESULTS_DIR, write_csv

DB_PATH = PROCESSED_DIR / "credit_risk.db"
DIMENSION_TABLES = [
    "dim_age_band",
    "dim_education",
    "dim_marriage",
    "dim_limit_band",
    "dim_pay_status",
    "dim_risk_band",
]


def query_rows(connection: sqlite3.Connection, query_name: str) -> list[tuple]:
    sql = (PROJECT_ROOT / "sql" / query_name).read_text(encoding="utf-8")
    return connection.execute(sql).fetchall()


def compare_value(rows: list[dict], indicator: str, dimension: str, python_value: float, sql_value: float, tolerance: float = 1e-8) -> None:
    difference = float(sql_value) - float(python_value)
    passed = math.isclose(float(sql_value), float(python_value), rel_tol=tolerance, abs_tol=tolerance)
    rows.append(
        {
            "indicator": indicator,
            "dimension": dimension,
            "python_value": float(python_value),
            "sql_value": float(sql_value),
            "difference_sql_minus_python": difference,
            "tolerance": tolerance,
            "status": "PASS" if passed else "FAIL",
        }
    )


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript((PROJECT_ROOT / "sql" / "schema.sql").read_text(encoding="utf-8"))
        for table_name in DIMENSION_TABLES:
            pd.read_csv(PROCESSED_DIR / f"{table_name}.csv").to_sql(table_name, connection, if_exists="append", index=False)
        pd.read_csv(PROCESSED_DIR / "model_scorecard.csv").to_sql("model_scorecard", connection, if_exists="append", index=False)
        pd.read_csv(PROCESSED_DIR / "fact_clients.csv").to_sql("fact_clients", connection, if_exists="append", index=False)
        foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_key_errors:
            raise RuntimeError(f"Échec d’intégrité des clés étrangères : {foreign_key_errors[:5]}")

        parity: list[dict] = []
        kpi = pd.read_csv(RESULTS_DIR / "portfolio_kpis.csv").iloc[0]
        global_sql = query_rows(connection, "01_global_default_rate.sql")[0]
        compare_value(parity, "Nombre de clients", "Total", float(kpi["clients"]), float(global_sql[0]), 0)
        compare_value(parity, "Nombre de défauts", "Total", float(kpi["defaulters"]), float(global_sql[1]), 0)
        compare_value(parity, "Taux de défaut", "Total", float(kpi["default_rate"]), float(global_sql[2]))

        exposure_sql = query_rows(connection, "03_defaulter_exposure.sql")[0]
        compare_value(parity, "Exposition des défaillants", "Total", float(kpi["defaulter_credit_limit_exposure_ntd"]), float(exposure_sql[0]), 1e-6)
        compare_value(parity, "Limite de crédit totale", "Total", float(kpi["total_credit_limit_ntd"]), float(exposure_sql[1]), 1e-6)

        age_python = pd.read_csv(RESULTS_DIR / "default_by_segment.csv")
        age_python = age_python.loc[age_python["segment_type"] == "Âge"].set_index("segment")
        for age_key, label, clients, defaults, rate, exposure in query_rows(connection, "02_default_rate_by_age_band.sql"):
            expected = age_python.loc[label]
            compare_value(parity, "Taux de défaut", f"Âge {label}", float(expected["default_rate"]), float(rate))
            compare_value(parity, "Exposition des défaillants", f"Âge {label}", float(expected["defaulter_limit_exposure"]), float(exposure), 1e-6)

        pay_python = pd.read_csv(RESULTS_DIR / "default_rate_by_pay0.csv").set_index("pay_code")
        for pay_code, label, clients, defaults, rate in query_rows(connection, "04_default_rate_by_pay0.sql"):
            expected = pay_python.loc[pay_code]
            compare_value(parity, "Taux de défaut", f"pay_0={pay_code}", float(expected["default_rate"]), float(rate))

        risk_python = pd.read_csv(RESULTS_DIR / "risk_band_summary.csv").set_index("risk_band_key")
        for risk_key, label, clients, defaults, rate, exposure in query_rows(connection, "05_default_rate_by_risk_band.sql"):
            expected = risk_python.loc[risk_key]
            compare_value(parity, "Taux de défaut", f"Partition Test · {label}", float(expected["default_rate"]), float(rate))
            compare_value(parity, "Exposition facturée positive", f"Partition Test · {label}", float(expected["positive_bill_exposure_ntd"]), float(exposure), 1e-6)

        parity_frame = pd.DataFrame(parity)
        write_csv(parity_frame, RESULTS_DIR / "sql_parity.csv")
        if (parity_frame["status"] != "PASS").any():
            failures = parity_frame.loc[parity_frame["status"] != "PASS"].to_dict(orient="records")
            raise RuntimeError(f"La parité SQL/Python a échoué : {failures[:5]}")
        table_count = connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table'").fetchone()[0]
        fact_count = connection.execute("SELECT COUNT(*) FROM fact_clients").fetchone()[0]
    print(f"SQLite reconstruit : {table_count} tables, {fact_count} clients; {len(parity)} comparaisons PASS.")


if __name__ == "__main__":
    main()
