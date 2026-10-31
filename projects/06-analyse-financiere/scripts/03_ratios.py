"""Synthèse des ratios, seuils de lecture, recommandations et signaux d'alerte."""
from __future__ import annotations

import pandas as pd

from pipeline_utils import FY_END, FY_START, ROOT, cagr, fr_num, fr_pct, fr_ratio


ALERTS = [
    {"alert_key": "operating_margin", "label_fr": "Marge opérationnelle", "threshold": 0.40,
     "direction": "at_least", "unit": "proportion",
     "definition": "Seuil de lecture interne : marge opérationnelle au moins égale à 40 %."},
    {"alert_key": "current_ratio", "label_fr": "Liquidité courante", "threshold": 1.0,
     "direction": "at_least", "unit": "ratio",
     "definition": "Seuil de lecture interne : actif courant au moins égal au passif courant."},
    {"alert_key": "debt_ratio", "label_fr": "Ratio d'endettement global", "threshold": 0.80,
     "direction": "at_most", "unit": "proportion",
     "definition": "Seuil de lecture interne : passif inférieur ou égal à 80 % du total de l'actif."},
    {"alert_key": "interest_coverage", "label_fr": "Couverture des intérêts", "threshold": 8.0,
     "direction": "at_least", "unit": "ratio",
     "definition": "Seuil de lecture interne : résultat d'exploitation au moins huit fois la charge d'intérêts."},
    {"alert_key": "fcf", "label_fr": "Flux de trésorerie disponible", "threshold": 0.0,
     "direction": "at_least", "unit": "USD",
     "definition": "Seuil de lecture interne : flux disponible positif."},
    {"alert_key": "revenue_growth", "label_fr": "Croissance des produits", "threshold": 0.0,
     "direction": "at_least", "unit": "proportion",
     "definition": "Seuil de lecture interne : croissance annuelle des produits positive."},
]


def main() -> None:
    results = ROOT / "results"
    annual = pd.read_csv(results / "annual_kpis.csv").set_index("fiscal_year")
    summary = pd.read_csv(results / "ratio_summary.csv").set_index("ratio_key")
    growth = pd.read_csv(results / "growth_summary.csv").set_index("metric")
    latest_year = int(annual.index.max())
    prior_year = int(annual.index.max() - 1)
    latest = annual.loc[latest_year]
    prior = annual.loc[prior_year]

    scorecard = pd.DataFrame([{
        "entity": "Mastercard Incorporated",
        "latest_year": latest_year,
        "revenue": float(latest["revenue"]),
        "operating_income": float(latest["operating_income"]),
        "net_income": float(latest["net_income"]),
        "operating_margin": float(latest["operating_margin"]),
        "net_margin": float(latest["net_margin"]),
        "roe": float(latest["roe"]),
        "roa": float(latest["roa"]),
        "current_ratio": float(latest["current_ratio"]),
        "debt_ratio": float(latest["debt_ratio"]),
        "fcf": float(latest["fcf"]),
        "fcf_margin": float(latest["fcf_margin"]),
        "eps_diluted": float(latest["eps_diluted"]),
        "revenue_cagr": float(cagr(annual["revenue"])),
        "net_income_cagr": float(cagr(annual["net_income"])),
        "period_start": FY_START, "period_end": FY_END,
    }])
    scorecard.to_csv(results / "financial_scorecard.csv", index=False, encoding="utf-8", float_format="%.10f")
    scorecard.to_csv(ROOT / "data/processed/financial_scorecard.csv", index=False, encoding="utf-8",
                     float_format="%.10f")

    alert_rows = []
    for definition in ALERTS:
        key = definition["alert_key"]
        observed = float(latest[key])
        if definition["direction"] == "at_least":
            ok = observed >= definition["threshold"]
        else:
            ok = observed <= definition["threshold"]
        alert_rows.append({
            "alert_key": key, "label_fr": definition["label_fr"], "unit": definition["unit"],
            "threshold": definition["threshold"], "observed": observed,
            "status": "CONFORME" if ok else "VIGILANCE",
            "definition": definition["definition"],
        })
    alerts = pd.DataFrame(alert_rows)
    alerts.to_csv(results / "alerts.csv", index=False, encoding="utf-8", float_format="%.10f")
    alerts.to_csv(ROOT / "data/processed/financial_alerts.csv", index=False, encoding="utf-8",
                  float_format="%.10f")

    coverage = pd.DataFrame([
        {"field": "segmentation par activité", "available": False,
         "handling": "La source companyfacts ne détaille pas les segments; aucune marge par activité n'est calculée."},
        {"field": "répartition géographique", "available": False,
         "handling": "Aucune ventilation régionale dans le fichier; la croissance n'est pas décomposée par zone."},
        {"field": "détail des rachats d'actions", "available": False,
         "handling": "Les rachats expliquent la baisse des capitaux propres mais leur montant annuel n'est pas extrait ici."},
        {"field": "intérêts minoritaires", "available": False,
         "handling": "L'écart résiduel de bilan n'est pas rattaché à une ligne; il n'est pas interprété."},
    ])
    coverage.to_csv(results / "coverage_gaps.csv", index=False, encoding="utf-8")

    op_margin = float(latest["operating_margin"])
    op_margin_prior = float(prior["operating_margin"])
    current_ratio = float(latest["current_ratio"])
    current_ratio_first = float(annual["current_ratio"].iloc[0])
    debt_ratio = float(latest["debt_ratio"])
    debt_ratio_first = float(annual["debt_ratio"].iloc[0])
    interest_cov = float(summary.loc["interest_coverage", "last_value"])
    fcf_margin = float(latest["fcf_margin"])
    capex_intensity = float(summary.loc["capex_intensity", "last_value"])
    revenue_cagr = float(growth.loc["revenue", "cagr"])
    last_growth = float(growth.loc["revenue", "last_year_growth"])

    recommendations = [
        {
            "priority": 1,
            "recommendation": "Protéger la marge opérationnelle en pilotant la croissance des charges d'exploitation sous celle des produits; conserver le seuil de 40 % comme repère de lecture.",
            "evidence": (f"Marge opérationnelle {fr_pct(op_margin)} en {latest_year} contre {fr_pct(op_margin_prior)} en {prior_year}; "
                         f"produits {fr_num(latest['revenue'])} USD et résultat d'exploitation {fr_num(latest['operating_income'])} USD."),
            "limitation": "La marge dépend du mix d'activités, non détaillé dans la source; aucun effet causal n'est établi.",
            "source_results": "results/annual_kpis.csv; results/ratio_summary.csv",
        },
        {
            "priority": 2,
            "recommendation": "Renforcer le coussin de liquidité: maintenir un ratio de liquidité courante au moins égal à 1,0 et documenter un plan de trésorerie si le passif courant continue de progresser plus vite que l'actif courant.",
            "evidence": (f"Liquidité courante {fr_ratio(current_ratio)} en {latest_year} contre {fr_ratio(current_ratio_first)} en {FY_START}; "
                         f"trésorerie {fr_num(latest['cash'])} USD."),
            "limitation": "Le ratio de liquidité courante inclut des actifs non immédiatement disponibles; il ne mesure pas un besoin de trésorerie daté.",
            "source_results": "results/annual_kpis.csv; results/ratio_summary.csv",
        },
        {
            "priority": 3,
            "recommendation": "Surveiller le levier financier et la couverture des intérêts lors de chaque nouvelle émission de dette; la baisse des capitaux propres réduit la marge de manœuvre.",
            "evidence": (f"Passif/actif {fr_pct(debt_ratio)} en {latest_year} contre {fr_pct(debt_ratio_first)} en {FY_START}; "
                         f"couverture des intérêts {fr_ratio(interest_cov, 1)}x."),
            "limitation": "La structure du passif (dette court/long terme, échéances) n'est pas extraite; le levier est un indicateur de synthèse.",
            "source_results": "results/annual_kpis.csv; results/ratio_summary.csv",
        },
        {
            "priority": 4,
            "recommendation": "Allouer le flux de trésorerie disponible en priorisant la réduction du levier lorsque la couverture des intérêts se dégrade, puis les rachats d'actions.",
            "evidence": (f"Flux disponible {fr_num(latest['fcf'])} USD, soit {fr_pct(fcf_margin)} des produits; "
                         f"intensité des investissements {fr_pct(capex_intensity)}."),
            "limitation": "Les rachats d'actions et dividendes ne sont pas quantifiés dans cette extraction; l'allocation n'est pas simulée.",
            "source_results": "results/annual_kpis.csv; results/ratio_summary.csv",
        },
        {
            "priority": 5,
            "recommendation": "Confirmer la durabilité de la croissance: la trajectoire récente doit être suivie sur des exercices complets, sans extrapoler un rythme annuel au-delà de la période observée.",
            "evidence": (f"Croissance annuelle des produits {fr_pct(revenue_cagr)} en moyenne {FY_START}-{FY_END}; "
                         f"dernière variation {fr_pct(last_growth)}."),
            "limitation": "Sept exercices seulement et aucune ventilation par segment; la croissance passée ne garantit pas la croissance future.",
            "source_results": "results/growth_summary.csv; results/reference_comparison.csv",
        },
    ]
    pd.DataFrame(recommendations).to_csv(results / "recommendations.csv", index=False, encoding="utf-8")

    category = summary.reset_index()[["ratio_key", "label_fr", "category", "last_value", "mean", "change_absolute"]]
    category.to_csv(results / "ratio_category_summary.csv", index=False, encoding="utf-8", float_format="%.10f")

    print(f"Fiche {latest_year} : marge opérationnelle {fr_pct(op_margin)}; ROE {fr_pct(latest['roe'])}; "
          f"liquidité {fr_ratio(current_ratio)}; dette/actif {fr_pct(debt_ratio)}.")
    print(f"Alertes : {int(alerts['status'].eq('CONFORME').sum())}/{len(alerts)} conformes; "
          f"{len(recommendations)} recommandations générées.")


if __name__ == "__main__":
    main()
