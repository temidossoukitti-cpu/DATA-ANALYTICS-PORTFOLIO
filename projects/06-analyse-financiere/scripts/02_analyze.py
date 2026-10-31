"""Analyse descriptive des états financiers Mastercard et graphiques de tendance."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pipeline_utils import (
    FY_END, FY_START, RATIOS, ROOT, cagr, compute_ratios, facts_to_metrics_matrix, load_facts,
)

BLUE = "#315a7d"
GOLD = "#c69214"
GRAY = "#7b8794"


def style_axis(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.2, linewidth=0.7)
    ax.set_axisbelow(True)


def main() -> None:
    facts = load_facts()
    matrix = facts_to_metrics_matrix(facts)
    ratios = compute_ratios(matrix)
    results = ROOT / "results"
    visuals = ROOT / "visuals"
    results.mkdir(exist_ok=True)
    visuals.mkdir(exist_ok=True)

    annual = pd.DataFrame(index=matrix.index)
    for key in ("revenue", "operating_income", "net_income", "eps_diluted", "cfo", "capex", "cash",
                "total_assets", "total_liabilities", "equity", "current_assets", "current_liabilities"):
        annual[key] = matrix[key]
    for key in ("operating_margin", "net_margin", "effective_tax_rate", "roe", "roa", "asset_turnover",
                "current_ratio", "cash_ratio", "debt_ratio", "equity_ratio", "leverage",
                "interest_coverage", "cfo_margin", "fcf", "fcf_margin", "capex_intensity",
                "revenue_growth", "net_income_growth", "eps_growth"):
        annual[key] = ratios[key]
    annual.reset_index().to_csv(results / "annual_kpis.csv", index=False, encoding="utf-8", float_format="%.10f")

    summary_rows = []
    for definition in RATIOS:
        key = definition["ratio_key"]
        series = ratios[key].dropna()
        first, last = float(series.iloc[0]), float(series.iloc[-1])
        change = last - first
        direction = "hausse" if change > 1e-12 else "baisse" if change < -1e-12 else "stable"
        summary_rows.append({
            "ratio_key": key, "label_fr": definition["label_fr"], "category": definition["category"],
            "unit": definition["unit"], "first_year": int(series.index[0]), "first_value": first,
            "last_year": int(series.index[-1]), "last_value": last, "change_absolute": change,
            "change_relative": change / abs(first) if first else np.nan,
            "mean": float(series.mean()), "minimum": float(series.min()), "maximum": float(series.max()),
            "direction": direction,
        })
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(results / "ratio_summary.csv", index=False, encoding="utf-8", float_format="%.10f")

    growth_rows = []
    for metric, label in [("revenue", "Produits"), ("net_income", "Résultat net"),
                          ("eps_diluted", "BPA dilué"), ("cfo", "Flux de trésorerie d'exploitation")]:
        series = matrix[metric]
        growth_rows.append({
            "metric": metric, "label_fr": label,
            "first_year": int(series.index[0]), "first_value": float(series.iloc[0]),
            "last_year": int(series.index[-1]), "last_value": float(series.iloc[-1]),
            "cagr": cagr(series), "last_year_growth": float(series.pct_change().iloc[-1]),
        })
    growth = pd.DataFrame(growth_rows)
    growth.to_csv(results / "growth_summary.csv", index=False, encoding="utf-8", float_format="%.10f")

    comparison_rows = []
    for definition in RATIOS:
        key = definition["ratio_key"]
        series = ratios[key].dropna()
        last = float(series.iloc[-1])
        prior = float(series.iloc[-2]) if len(series) > 1 else np.nan
        mean = float(series.mean())
        comparison_rows.append({
            "ratio_key": key, "label_fr": definition["label_fr"], "unit": definition["unit"],
            "latest_year": int(series.index[-1]), "latest_value": last,
            "prior_year": int(series.index[-2]) if len(series) > 1 else np.nan, "prior_value": prior,
            "change_vs_prior": last - prior if not np.isnan(prior) else np.nan,
            "mean_2019_2025": mean, "gap_vs_mean": last - mean,
        })
    pd.DataFrame(comparison_rows).to_csv(results / "reference_comparison.csv", index=False,
                                         encoding="utf-8", float_format="%.10f")

    years = matrix.index.to_list()
    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    ax.bar([str(y) for y in years], matrix["revenue"] / 1e9, color=BLUE, width=0.62,
           label="Produits")
    ax.plot([str(y) for y in years], matrix["operating_income"] / 1e9, color=GOLD, marker="o",
            linewidth=2, label="Résultat d'exploitation")
    ax.set_title("Produits et résultat d'exploitation (milliards USD)")
    ax.set_xlabel("Exercice comptable")
    ax.set_ylabel("Milliards USD")
    ax.legend(frameon=False)
    style_axis(ax); fig.tight_layout(); fig.savefig(visuals / "revenue_trend.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    ax.plot([str(y) for y in years], ratios["operating_margin"] * 100, color=BLUE, marker="o",
            linewidth=2, label="Marge opérationnelle")
    ax.plot([str(y) for y in years], ratios["net_margin"] * 100, color=GOLD, marker="s",
            linewidth=2, label="Marge nette")
    ax.set_title("Marges opérationnelle et nette")
    ax.set_xlabel("Exercice comptable")
    ax.set_ylabel("% des produits")
    ax.legend(frameon=False)
    style_axis(ax); fig.tight_layout(); fig.savefig(visuals / "margin_trend.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    ax.plot([str(y) for y in years], ratios["roe"] * 100, color=BLUE, marker="o",
            linewidth=2, label="ROE")
    ax.plot([str(y) for y in years], ratios["roa"] * 100, color=GOLD, marker="s",
            linewidth=2, label="ROA")
    ax.set_title("Rentabilité des capitaux propres et de l'actif")
    ax.set_xlabel("Exercice comptable")
    ax.set_ylabel("%")
    ax.legend(frameon=False)
    style_axis(ax); fig.tight_layout(); fig.savefig(visuals / "roe_roa_trend.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    ax.plot([str(y) for y in years], ratios["current_ratio"], color=BLUE, marker="o",
            linewidth=2, label="Liquidité courante")
    ax.plot([str(y) for y in years], ratios["cash_ratio"], color=GOLD, marker="s",
            linewidth=2, label="Trésorerie / passif courant")
    ax.axhline(1.0, color=GRAY, linestyle="--", linewidth=1, label="Seuil de référence 1,0")
    ax.set_title("Ratios de liquidité")
    ax.set_xlabel("Exercice comptable")
    ax.set_ylabel("Ratio (x)")
    ax.legend(frameon=False)
    style_axis(ax); fig.tight_layout(); fig.savefig(visuals / "liquidity_trend.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    ax.plot([str(y) for y in years], ratios["debt_ratio"] * 100, color=BLUE, marker="o",
            linewidth=2, label="Passif / actif")
    ax.plot([str(y) for y in years], ratios["equity_ratio"] * 100, color=GOLD, marker="s",
            linewidth=2, label="Capitaux propres / actif")
    ax.set_title("Structure financière")
    ax.set_xlabel("Exercice comptable")
    ax.set_ylabel("% du total de l'actif")
    ax.legend(frameon=False)
    style_axis(ax); fig.tight_layout(); fig.savefig(visuals / "leverage_trend.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    ax.bar([str(y) for y in years], matrix["cfo"] / 1e9, color=BLUE, width=0.62, label="Flux d'exploitation")
    ax.bar([str(y) for y in years], -matrix["capex"] / 1e9, color=GOLD, width=0.62, label="Capex (décaissement)")
    ax.plot([str(y) for y in years], ratios["fcf"] / 1e9, color=GRAY, marker="o",
            linewidth=2, label="Flux disponible")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Flux de trésorerie (milliards USD)")
    ax.set_xlabel("Exercice comptable")
    ax.set_ylabel("Milliards USD")
    ax.legend(frameon=False)
    style_axis(ax); fig.tight_layout(); fig.savefig(visuals / "cashflow_trend.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    growth_series = ratios["revenue_growth"].dropna() * 100
    bars = ax.bar([str(y) for y in growth_series.index], growth_series, color=BLUE, width=0.62)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Croissance annuelle des produits")
    ax.set_xlabel("Exercice comptable")
    ax.set_ylabel("%")
    for bar, value in zip(bars, growth_series):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{value:.1f}%", ha="center", va="bottom" if value >= 0 else "top", fontsize=9)
    style_axis(ax); fig.tight_layout(); fig.savefig(visuals / "growth_trend.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    ax.plot([str(y) for y in years], ratios["fcf_margin"] * 100, color=BLUE, marker="o",
            linewidth=2, label="Marge de flux disponible")
    ax.plot([str(y) for y in years], ratios["cfo_margin"] * 100, color=GOLD, marker="s",
            linewidth=2, label="Marge d'exploitation de trésorerie")
    ax.set_title("Qualité de conversion en trésorerie")
    ax.set_xlabel("Exercice comptable")
    ax.set_ylabel("% des produits")
    ax.legend(frameon=False)
    style_axis(ax); fig.tight_layout(); fig.savefig(visuals / "fcf_margin_trend.png", dpi=160); plt.close(fig)

    print(f"Analyse : {len(years)} exercices ({FY_START}-{FY_END}); "
          f"produits {matrix['revenue'].iloc[-1]/1e9:.2f} Md USD; "
          f"marge opérationnelle {ratios['operating_margin'].iloc[-1]:.2%}.")
    print(f"ROE {ratios['roe'].iloc[-1]:.2%}; liquidité courante {ratios['current_ratio'].iloc[-1]:.2f}; "
          f"8 graphiques générés.")


if __name__ == "__main__":
    main()
