"""Construit la base SQLite et vérifie la parité des métriques Python/SQL."""
from __future__ import annotations

import sqlite3

import pandas as pd

from pipeline_utils import ROOT


def run_query(connection: sqlite3.Connection, name: str) -> pd.DataFrame:
    sql = (ROOT / "sql" / name).read_text(encoding="utf-8")
    return pd.read_sql_query(sql, connection)


def main() -> None:
    processed = ROOT / "data/processed"
    database = processed / "mastercard_financials.db"
    database.unlink(missing_ok=True)
    connection = sqlite3.connect(database)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript((ROOT / "sql/schema.sql").read_text(encoding="utf-8"))

    table_files = {
        "dim_fiscal_year": processed / "dim_fiscal_year.csv",
        "dim_metric": processed / "dim_metric.csv",
        "dim_ratio": processed / "dim_ratio.csv",
        "fact_financials": processed / "fact_financials.csv",
        "fact_ratios": processed / "fact_ratios.csv",
        "financial_scorecard": processed / "financial_scorecard.csv",
        "financial_alerts": processed / "financial_alerts.csv",
    }
    columns = {
        "dim_fiscal_year": ["fiscal_year_key", "period_end", "label_fr", "sort_order"],
        "dim_metric": ["metric_key", "label_fr", "statement", "unit", "definition", "sort_order"],
        "dim_ratio": ["ratio_key", "label_fr", "category", "unit", "definition", "formula", "sort_order"],
        "fact_financials": ["fiscal_year_key", "metric_key", "value"],
        "fact_ratios": ["fiscal_year_key", "ratio_key", "value"],
        "financial_scorecard": ["entity", "latest_year", "revenue", "operating_income", "net_income",
                                "operating_margin", "net_margin", "roe", "roa", "current_ratio",
                                "debt_ratio", "fcf", "fcf_margin", "eps_diluted", "revenue_cagr",
                                "net_income_cagr", "period_start", "period_end"],
        "financial_alerts": ["alert_key", "label_fr", "unit", "threshold", "observed", "status", "definition"],
    }
    for table, path in table_files.items():
        frame = pd.read_csv(path)
        if table == "dim_fiscal_year":
            frame = frame.rename(columns={"fiscal_year": "fiscal_year_key"})
        frame[columns[table]].to_sql(table, connection, if_exists="append", index=False)

    foreign_key_errors = 0
    for table in ("fact_financials", "fact_ratios"):
        foreign_key_errors += len(connection.execute(f"PRAGMA foreign_key_check({table})").fetchall())
    if foreign_key_errors:
        connection.close()
        raise SystemExit(f"Échec d'intégrité référentielle SQLite : {foreign_key_errors} ligne(s).")

    latest_sql = run_query(connection, "01_latest_kpis.sql").set_index("indicateur")
    ratios_sql = run_query(connection, "02_ratios_by_year.sql").set_index("fiscal_year")
    margins_sql = run_query(connection, "03_margin_trend.sql").set_index("fiscal_year")
    growth_sql = run_query(connection, "04_growth_yoy.sql").set_index("fiscal_year")
    comparison_sql = run_query(connection, "05_latest_vs_average.sql").set_index("ratio")
    connection.close()

    annual = pd.read_csv(ROOT / "results/annual_kpis.csv").set_index("fiscal_year")
    comparison = pd.read_csv(ROOT / "results/reference_comparison.csv").set_index("label_fr")
    parity = []

    def compare(name: str, py_value: float, sql_value: float, tolerance: float) -> None:
        py_value, sql_value = float(py_value), float(sql_value)
        difference = abs(py_value - sql_value)
        parity.append({"indicator": name, "python_value": py_value, "sql_value": sql_value,
                       "absolute_difference": difference, "tolerance": tolerance,
                       "status": "PASS" if difference <= tolerance else "FAIL"})

    latest_year = int(annual.index.max())
    label_map = {
        "revenue": "Produits", "operating_income": "Résultat d'exploitation",
        "net_income": "Résultat net", "eps_diluted": "BPA dilué",
        "total_assets": "Total actif", "total_liabilities": "Total passif",
        "equity": "Capitaux propres", "cfo": "Flux de trésorerie d'exploitation",
        "capex": "Investissements corporels",
    }
    for metric, label in label_map.items():
        tolerance = 1e-9 if metric == "eps_diluted" else 0.01
        compare(f"latest.{metric}", annual.loc[latest_year, metric], latest_sql.loc[label, "valeur"], tolerance)

    for metric, column in [("operating_margin", "marge_operationnelle"), ("net_margin", "marge_nette"),
                           ("roe", "roe"), ("roa", "roa"),
                           ("current_ratio", "liquidite_courante"), ("debt_ratio", "dette_sur_actif")]:
        for year, row in ratios_sql.iterrows():
            compare(f"ratios.{int(year)}.{metric}", annual.loc[int(year), metric], row[column], 1e-6)

    for year, row in margins_sql.iterrows():
        compare(f"margins.{int(year)}.operating_margin", annual.loc[int(year), "operating_margin"],
                row["marge_operationnelle"], 1e-6)
        compare(f"margins.{int(year)}.net_margin", annual.loc[int(year), "net_margin"],
                row["marge_nette"], 1e-6)
        compare(f"margins.{int(year)}.effective_tax_rate", annual.loc[int(year), "effective_tax_rate"],
                row["taux_imposition_effectif"], 1e-6)

    for year, row in growth_sql.iterrows():
        if int(year) == int(growth_sql.index.min()):
            continue
        for metric, column in [("revenue_growth", "croissance_produits"),
                               ("net_income_growth", "croissance_resultat_net"),
                               ("eps_growth", "croissance_bpa")]:
            compare(f"growth.{int(year)}.{metric}", annual.loc[int(year), metric], row[column], 1e-6)

    for label, row in comparison_sql.iterrows():
        compare(f"comparison.{label}.gap_vs_mean", comparison.loc[label, "gap_vs_mean"],
                row["ecart"], 1e-6)

    parity_frame = pd.DataFrame(parity)
    parity_frame.to_csv(ROOT / "results/sql_parity.csv", index=False, encoding="utf-8")
    if (parity_frame["status"] != "PASS").any():
        failed = parity_frame.loc[parity_frame["status"] != "PASS",
                                  ["indicator", "python_value", "sql_value", "absolute_difference", "tolerance"]]
        print(failed.to_string(index=False))
        raise SystemExit("La parité Python/SQL contient des échecs; consulter results/sql_parity.csv.")
    print(f"SQLite recréée: {database.stat().st_size:,} octets; intégrité référentielle PASS.")
    print(f"Parité Python/SQL: {len(parity_frame)} indicateurs comparés, 0 échec(s).")


if __name__ == "__main__":
    main()
