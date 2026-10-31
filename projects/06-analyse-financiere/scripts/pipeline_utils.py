"""Fonctions communes au pipeline d'analyse financière Mastercard."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent
RAW_FILE = ROOT / "data/raw/mastercard_companyfacts.json"
FY_START = 2019
FY_END = 2025

METRICS = [
    {"metric_key": "revenue", "label_fr": "Produits", "tags": ["Revenues"], "unit": "USD",
     "statement": "Compte de résultat", "definition": "Produits totaux annuels (US-GAAP Revenues).", "sort_order": 1},
    {"metric_key": "operating_income", "label_fr": "Résultat d'exploitation", "tags": ["OperatingIncomeLoss"], "unit": "USD",
     "statement": "Compte de résultat", "definition": "Résultat d'exploitation annuel (US-GAAP OperatingIncomeLoss).", "sort_order": 2},
    {"metric_key": "net_income", "label_fr": "Résultat net", "tags": ["ProfitLoss"], "unit": "USD",
     "statement": "Compte de résultat", "definition": "Résultat net attribuable au groupe (US-GAAP ProfitLoss).", "sort_order": 3},
    {"metric_key": "income_tax", "label_fr": "Charge d'impôt", "tags": ["IncomeTaxExpenseBenefit"], "unit": "USD",
     "statement": "Compte de résultat", "definition": "Charge d'impôt sur le résultat (US-GAAP IncomeTaxExpenseBenefit).", "sort_order": 4},
    {"metric_key": "interest_expense", "label_fr": "Charge d'intérêts", "tags": ["InterestExpenseNonoperating", "InterestExpense"], "unit": "USD",
     "statement": "Compte de résultat", "definition": "Charge d'intérêts annuelle; InterestExpenseNonoperating prioritaire, InterestExpense en secours.", "sort_order": 5},
    {"metric_key": "total_assets", "label_fr": "Total actif", "tags": ["Assets"], "unit": "USD",
     "statement": "Bilan", "definition": "Total de l'actif au 31 décembre.", "sort_order": 6},
    {"metric_key": "total_liabilities", "label_fr": "Total passif", "tags": ["Liabilities"], "unit": "USD",
     "statement": "Bilan", "definition": "Total du passif au 31 décembre.", "sort_order": 7},
    {"metric_key": "equity", "label_fr": "Capitaux propres", "tags": ["StockholdersEquity"], "unit": "USD",
     "statement": "Bilan", "definition": "Capitaux propres attribuables aux actionnaires au 31 décembre.", "sort_order": 8},
    {"metric_key": "current_assets", "label_fr": "Actif courant", "tags": ["AssetsCurrent"], "unit": "USD",
     "statement": "Bilan", "definition": "Actif courant au 31 décembre.", "sort_order": 9},
    {"metric_key": "current_liabilities", "label_fr": "Passif courant", "tags": ["LiabilitiesCurrent"], "unit": "USD",
     "statement": "Bilan", "definition": "Passif courant au 31 décembre.", "sort_order": 10},
    {"metric_key": "cash", "label_fr": "Trésorerie et équivalents", "tags": ["CashAndCashEquivalentsAtCarryingValue"], "unit": "USD",
     "statement": "Bilan", "definition": "Trésorerie et équivalents de trésorerie au 31 décembre.", "sort_order": 11},
    {"metric_key": "cfo", "label_fr": "Flux de trésorerie d'exploitation", "tags": ["NetCashProvidedByUsedInOperatingActivities"], "unit": "USD",
     "statement": "Flux de trésorerie", "definition": "Flux net de trésorerie lié aux activités opérationnelles.", "sort_order": 12},
    {"metric_key": "capex", "label_fr": "Investissements corporels", "tags": ["PaymentsToAcquirePropertyPlantAndEquipment"], "unit": "USD",
     "statement": "Flux de trésorerie", "definition": "Décaissements pour acquisitions d'immobilisations corporelles (capex).", "sort_order": 13},
    {"metric_key": "eps_diluted", "label_fr": "BPA dilué", "tags": ["EarningsPerShareDiluted"], "unit": "USD par action",
     "statement": "Compte de résultat", "definition": "Bénéfice par action dilué déclaré.", "sort_order": 14},
    {"metric_key": "diluted_shares", "label_fr": "Actions diluées moyennes", "tags": ["WeightedAverageNumberOfDilutedSharesOutstanding"], "unit": "actions",
     "statement": "Compte de résultat", "definition": "Nombre moyen pondéré d'actions diluées.", "sort_order": 15},
]

RATIOS = [
    {"ratio_key": "operating_margin", "label_fr": "Marge opérationnelle", "category": "Rentabilité", "unit": "proportion", "sort_order": 1,
     "definition": "Résultat d'exploitation divisé par les produits.",
     "formula": "operating_income / revenue"},
    {"ratio_key": "net_margin", "label_fr": "Marge nette", "category": "Rentabilité", "unit": "proportion", "sort_order": 2,
     "definition": "Résultat net divisé par les produits.",
     "formula": "net_income / revenue"},
    {"ratio_key": "effective_tax_rate", "label_fr": "Taux d'impôt effectif", "category": "Rentabilité", "unit": "proportion", "sort_order": 3,
     "definition": "Charge d'impôt divisée par le résultat avant impôt (résultat net + charge d'impôt).",
     "formula": "income_tax / (net_income + income_tax)"},
    {"ratio_key": "roa", "label_fr": "Rentabilité de l'actif (ROA)", "category": "Rentabilité", "unit": "proportion", "sort_order": 4,
     "definition": "Résultat net divisé par le total de l'actif de fin d'exercice.",
     "formula": "net_income / total_assets"},
    {"ratio_key": "roe", "label_fr": "Rentabilité des capitaux propres (ROE)", "category": "Rentabilité", "unit": "proportion", "sort_order": 5,
     "definition": "Résultat net divisé par les capitaux propres de fin d'exercice.",
     "formula": "net_income / equity"},
    {"ratio_key": "asset_turnover", "label_fr": "Rotation de l'actif", "category": "Efficacité", "unit": "ratio", "sort_order": 6,
     "definition": "Produits divisés par le total de l'actif; nombre d'unités de produits par unité d'actif.",
     "formula": "revenue / total_assets"},
    {"ratio_key": "current_ratio", "label_fr": "Ratio de liquidité courante", "category": "Liquidité", "unit": "ratio", "sort_order": 7,
     "definition": "Actif courant divisé par le passif courant.",
     "formula": "current_assets / current_liabilities"},
    {"ratio_key": "cash_ratio", "label_fr": "Ratio de trésorerie", "category": "Liquidité", "unit": "ratio", "sort_order": 8,
     "definition": "Trésorerie et équivalents divisés par le passif courant.",
     "formula": "cash / current_liabilities"},
    {"ratio_key": "debt_ratio", "label_fr": "Ratio d'endettement global", "category": "Structure", "unit": "proportion", "sort_order": 9,
     "definition": "Total du passif divisé par le total de l'actif.",
     "formula": "total_liabilities / total_assets"},
    {"ratio_key": "equity_ratio", "label_fr": "Part des capitaux propres", "category": "Structure", "unit": "proportion", "sort_order": 10,
     "definition": "Capitaux propres divisés par le total de l'actif.",
     "formula": "equity / total_assets"},
    {"ratio_key": "leverage", "label_fr": "Levier financier", "category": "Structure", "unit": "ratio", "sort_order": 11,
     "definition": "Total de l'actif divisé par les capitaux propres.",
     "formula": "total_assets / equity"},
    {"ratio_key": "interest_coverage", "label_fr": "Couverture des intérêts", "category": "Structure", "unit": "ratio", "sort_order": 12,
     "definition": "Résultat d'exploitation divisé par la charge d'intérêts.",
     "formula": "operating_income / interest_expense"},
    {"ratio_key": "cfo_margin", "label_fr": "Marge de trésorerie d'exploitation", "category": "Trésorerie", "unit": "proportion", "sort_order": 13,
     "definition": "Flux de trésorerie d'exploitation divisé par les produits.",
     "formula": "cfo / revenue"},
    {"ratio_key": "fcf", "label_fr": "Flux de trésorerie disponible", "category": "Trésorerie", "unit": "USD", "sort_order": 14,
     "definition": "Flux de trésorerie d'exploitation moins les investissements corporels.",
     "formula": "cfo - capex"},
    {"ratio_key": "fcf_margin", "label_fr": "Marge de flux disponible", "category": "Trésorerie", "unit": "proportion", "sort_order": 15,
     "definition": "Flux de trésorerie disponible divisé par les produits.",
     "formula": "(cfo - capex) / revenue"},
    {"ratio_key": "capex_intensity", "label_fr": "Intensité des investissements", "category": "Trésorerie", "unit": "proportion", "sort_order": 16,
     "definition": "Investissements corporels divisés par les produits.",
     "formula": "capex / revenue"},
    {"ratio_key": "revenue_growth", "label_fr": "Croissance des produits", "category": "Croissance", "unit": "proportion", "sort_order": 17,
     "definition": "Variation annuelle des produits par rapport à l'exercice précédent.",
     "formula": "revenue / revenue(t-1) - 1"},
    {"ratio_key": "net_income_growth", "label_fr": "Croissance du résultat net", "category": "Croissance", "unit": "proportion", "sort_order": 18,
     "definition": "Variation annuelle du résultat net par rapport à l'exercice précédent.",
     "formula": "net_income / net_income(t-1) - 1"},
    {"ratio_key": "eps_growth", "label_fr": "Croissance du BPA dilué", "category": "Croissance", "unit": "proportion", "sort_order": 19,
     "definition": "Variation annuelle du bénéfice par action dilué.",
     "formula": "eps_diluted / eps_diluted(t-1) - 1"},
]


def load_companyfacts() -> dict:
    if not RAW_FILE.is_file():
        raise FileNotFoundError(f"Fichier SEC companyfacts absent : {RAW_FILE}")
    with RAW_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _tag_series(facts: dict, tag: str, taxonomy: str) -> dict[int, float]:
    block = facts.get("facts", {}).get(taxonomy, {})
    if tag not in block:
        return {}
    series: dict[int, tuple[float, str]] = {}
    for entries in block[tag]["units"].values():
        for entry in entries:
            if entry.get("form") != "10-K" or entry.get("fp") != "FY":
                continue
            end = str(entry.get("end", ""))
            if not end.endswith("-12-31"):
                continue
            try:
                year = int(end[:4])
            except ValueError:
                continue
            if year < FY_START or year > FY_END:
                continue
            filed = str(entry.get("filed", ""))
            if year not in series or filed >= series[year][1]:
                series[year] = (float(entry["val"]), filed)
    return {year: value for year, (value, _) in series.items()}


def annual_series(facts: dict, tags: list[str], taxonomy: str = "us-gaap") -> dict[int, float]:
    """Série annuelle par exercice civil; le premier tag disponible prime, les suivants complètent."""
    series: dict[int, float] = {}
    for tag in tags:
        for year, value in _tag_series(facts, tag, taxonomy).items():
            series.setdefault(year, value)
    return series


def build_facts() -> pd.DataFrame:
    facts = load_companyfacts()
    rows = []
    for metric in METRICS:
        series = annual_series(facts, metric["tags"])
        for year in range(FY_START, FY_END + 1):
            if year not in series:
                raise ValueError(f"Valeur absente pour {metric['metric_key']} en {year}.")
            rows.append({
                "fiscal_year": year,
                "metric_key": metric["metric_key"],
                "value": float(series[year]),
                "unit": metric["unit"],
                "statement": metric["statement"],
                "definition": metric["definition"],
            })
    frame = pd.DataFrame(rows)
    expected = len(METRICS) * (FY_END - FY_START + 1)
    if len(frame) != expected:
        raise ValueError(f"Table de faits incomplète : {len(frame)} lignes au lieu de {expected}.")
    return frame


def facts_to_metrics_matrix(facts: pd.DataFrame) -> pd.DataFrame:
    if "fiscal_year_key" in facts.columns:
        facts = facts.rename(columns={"fiscal_year_key": "fiscal_year"})
    matrix = facts.pivot(index="fiscal_year", columns="metric_key", values="value").sort_index()
    return matrix


def compute_ratios(matrix: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=matrix.index)
    out["operating_margin"] = matrix["operating_income"] / matrix["revenue"]
    out["net_margin"] = matrix["net_income"] / matrix["revenue"]
    out["effective_tax_rate"] = matrix["income_tax"] / (matrix["net_income"] + matrix["income_tax"])
    out["roa"] = matrix["net_income"] / matrix["total_assets"]
    out["roe"] = matrix["net_income"] / matrix["equity"]
    out["asset_turnover"] = matrix["revenue"] / matrix["total_assets"]
    out["current_ratio"] = matrix["current_assets"] / matrix["current_liabilities"]
    out["cash_ratio"] = matrix["cash"] / matrix["current_liabilities"]
    out["debt_ratio"] = matrix["total_liabilities"] / matrix["total_assets"]
    out["equity_ratio"] = matrix["equity"] / matrix["total_assets"]
    out["leverage"] = matrix["total_assets"] / matrix["equity"]
    out["interest_coverage"] = matrix["operating_income"] / matrix["interest_expense"]
    out["cfo_margin"] = matrix["cfo"] / matrix["revenue"]
    out["fcf"] = matrix["cfo"] - matrix["capex"]
    out["fcf_margin"] = out["fcf"] / matrix["revenue"]
    out["capex_intensity"] = matrix["capex"] / matrix["revenue"]
    out["revenue_growth"] = matrix["revenue"].pct_change()
    out["net_income_growth"] = matrix["net_income"].pct_change()
    out["eps_growth"] = matrix["eps_diluted"].pct_change()
    return out


def cagr(series: pd.Series) -> float:
    values = series.dropna()
    if len(values) < 2 or values.iloc[0] <= 0:
        return float("nan")
    periods = len(values) - 1
    return float((values.iloc[-1] / values.iloc[0]) ** (1 / periods) - 1)


def load_facts() -> pd.DataFrame:
    path = ROOT / "data/processed/fact_financials.csv"
    if not path.is_file():
        raise FileNotFoundError(f"Table de faits absente : {path}")
    return pd.read_csv(path)


def fr_num(value: float, digits: int = 0) -> str:
    return f"{float(value):,.{digits}f}".replace(",", " ").replace(".", ",")


def fr_pct(value: float, digits: int = 2) -> str:
    return f"{float(value) * 100:.{digits}f}".replace(".", ",") + " %"


def fr_ratio(value: float, digits: int = 2) -> str:
    return f"{float(value):.{digits}f}".replace(".", ",")
