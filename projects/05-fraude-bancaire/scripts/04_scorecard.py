"""Synthèse des mesures, recommandations et visuels du modèle."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve

from pipeline_utils import ROOT, population_number

BLUE = "#315a7d"
GOLD = "#c69214"
GRAY = "#7b8794"


def style_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(alpha=0.2, linewidth=0.7)
    ax.set_axisbelow(True)


def main() -> None:
    results = ROOT / "results"
    visuals = ROOT / "visuals"
    metrics = pd.read_csv(results / "model_metrics.csv").set_index("method")
    money = pd.read_csv(results / "money_controls.csv").set_index("method")
    sensitivity = pd.read_csv(results / "cost_sensitivity.csv")
    amount_bands = pd.read_csv(results / "fraud_by_amount_band.csv")
    time_windows = pd.read_csv(results / "fraud_by_time_window.csv")
    type_gap = pd.read_csv(results / "fraud_by_transaction_type.csv")
    test = pd.read_csv(ROOT / "data/processed/fact_model_test.csv")
    population_rate = population_number("fraud_rate")
    model = metrics.loc["Modèle logistique"]
    baseline = metrics.loc["Règle montant P99"]
    model_cost = float(money.loc["Modèle logistique", "expected_cost_estimate"])
    baseline_cost = float(money.loc["Règle montant P99", "expected_cost_estimate"])
    cost_ratio = baseline_cost / model_cost if model_cost else np.nan
    high_amount = amount_bands.loc[amount_bands["group_key"].eq(4)].iloc[0]
    peak_time = time_windows.sort_values("fraud_rate", ascending=False).iloc[0]
    selected_thresholds = sorted(sensitivity["threshold_selected_on_training_oof"].unique())
    stable_threshold = len(selected_thresholds) == 1
    processed = ROOT / "data/processed"
    sensitivity.to_csv(processed / "model_cost_sensitivity.csv", index=False, encoding="utf-8")
    money.reset_index().to_csv(processed / "model_money_controls.csv", index=False, encoding="utf-8")

    assumptions = pd.DataFrame([
        {"assumption": "loss_severity_base", "value": 1.0, "unit": "part of Amount", "status": "ASSUMPTION", "definition": "Un frauduleux manqué est évalué à 100 % de Amount; les remboursements et pertes réellement recouvrées sont inconnus."},
        {"assumption": "legitimate_friction_base", "value": 10.0, "unit": "dataset amount units per legitimate flag", "status": "ASSUMPTION", "definition": "Coût proxy fixe d'une friction sur une transaction légitime; la devise n'est pas fournie par la source."},
        {"assumption": "loss_severity_sensitivity", "value": "0.5;1.0;1.5", "unit": "part of Amount", "status": "ASSUMPTION", "definition": "Trois scénarios de perte sur fraude manquée."},
        {"assumption": "friction_cost_sensitivity", "value": "5;10;25", "unit": "dataset amount units per legitimate flag", "status": "ASSUMPTION", "definition": "Trois coûts proxy de friction pour une alerte injustifiée."},
        {"assumption": "baseline_amount_rule", "value": float(baseline["amount_cutoff"]), "unit": "dataset amount units", "status": "RULE DE COMPARAISON", "definition": "Alerter si Amount atteint le 99e percentile pondéré du train légitime."},
        {"assumption": "model_threshold_grid", "value": 0.001, "unit": "probability step", "status": "CHOIX MÉTHODOLOGIQUE", "definition": "Seuil coût-minimal sélectionné sur les prédictions groupées hors pli du train; test réservé à l'évaluation."},
    ])
    assumptions.to_csv(results / "cost_assumptions.csv", index=False, encoding="utf-8")

    recommendations = [
        {
            "priority": 1,
            "recommendation": f"Tester le modèle logistique pondéré comme file de revue plutôt que bloquer automatiquement; seuil de risque {float(model['decision_threshold']):.3f}.",
            "evidence": f"Test pondéré: rappel {float(model['recall_weighted']):.1%}, précision {float(model['precision_weighted']):.1%}, PR-AUC {float(model['pr_auc_weighted']):.3f}.",
            "limitation": "Évaluation historique sur deux jours et caractéristiques V1–V28 anonymisées; validation temporelle ultérieure nécessaire.",
            "source_results": "results/model_metrics.csv; data/processed/model_scorecard.csv",
        },
        {
            "priority": 2,
            "recommendation": "Ne pas utiliser une règle montant seule comme contrôle principal; la réserver au triage secondaire des dossiers de montant élevé.",
            "evidence": f"Règle P99 à {float(baseline['amount_cutoff']):.2f} unités: rappel {float(baseline['recall_weighted']):.1%}; coût test estimé {baseline_cost:,.0f}, contre {model_cost:,.0f} pour le modèle (rapport {cost_ratio:.2f}×).",
            "limitation": "Les coûts sont des hypothèses; le seuil P99 est calculé sur les légitimes du train seulement.",
            "source_results": "results/model_metrics.csv; results/money_controls.csv",
        },
        {
            "priority": 3,
            "recommendation": "Prioriser une revue renforcée des transactions de plus de 200 unités du dataset, sans ignorer les petits montants.",
            "evidence": f"Bande >200: taux pondéré {float(high_amount['fraud_rate']):.3%} contre {population_rate:.3%} au total; {float(high_amount['fraud_transactions_estimate']):.0f} fraudes pondérées estimées.",
            "limitation": "Amount n'a pas de devise; les seuils sont descriptifs et non des règles optimisées de blocage.",
            "source_results": "results/fraud_by_amount_band.csv; results/population_kpis.csv",
        },
        {
            "priority": 4,
            "recommendation": "Surveiller la fenêtre relative de six heures ayant le taux le plus élevé, uniquement comme hypothèse à confirmer sur des périodes plus longues.",
            "evidence": f"{peak_time['label_fr']}: taux pondéré {float(peak_time['fraud_rate']):.3%}, soit {float(peak_time['fraud_rate'])/population_rate:.2f}× le taux global.",
            "limitation": "Fenêtre relative au premier enregistrement, seulement deux jours; aucune heure civile ni causalité ne peut être inférée.",
            "source_results": "results/fraud_by_time_window.csv; results/population_kpis.csv",
        },
        {
            "priority": 5,
            "recommendation": "Calibrer les coûts réels avant déploiement et collecter des champs métier; ne pas inférer un type de commerce à partir des composantes PCA.",
            "evidence": f"Sensibilité sur {len(sensitivity)} combinaisons; coût test de {sensitivity['test_expected_cost_estimate'].min():,.0f} à {sensitivity['test_expected_cost_estimate'].max():,.0f} unités; seuil {'stable à '+format(selected_thresholds[0], '.3f') if stable_threshold else 'variable selon le scénario'}. {type_gap.iloc[0]['availability']}: taux par type non calculable.",
            "limitation": "La devise, le coût de friction, le recouvrement et les variables d'origine de V1–V28 ne sont pas fournis.",
            "source_results": "results/cost_sensitivity.csv; results/cost_assumptions.csv; results/coverage_gaps.csv",
        },
    ]
    pd.DataFrame(recommendations).to_csv(results / "recommendations.csv", index=False, encoding="utf-8")

    # Precision-recall comparison, weighted to the known population class totals.
    y = test["outcome_key"].to_numpy(dtype=int)
    weights = test["eval_population_weight"].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(8.4, 5.8))
    for label, score, color in [
        ("Régression logistique pondérée", test["model_probability"].to_numpy(dtype=float), BLUE),
        ("Règle montant (score = Amount)", test["amount"].to_numpy(dtype=float), GOLD),
    ]:
        precision, recall, _ = precision_recall_curve(y, score, sample_weight=weights)
        ap = float(metrics.loc["Modèle logistique" if label.startswith("Régression") else "Règle montant P99", "pr_auc_weighted"])
        ax.plot(recall, precision, color=color, linewidth=2, label=f"{label} · PR-AUC {ap:.3f}")
    ax.axhline(population_rate, color=GRAY, linestyle="--", linewidth=1, label=f"Prévalence source {population_rate:.3%}")
    ax.set_title("Courbes précision-rappel pondérées — partition test")
    ax.set_xlabel("Rappel pondéré")
    ax.set_ylabel("Précision pondérée")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.legend(frameon=False, fontsize=8)
    style_axis(ax); fig.tight_layout(); fig.savefig(visuals / "precision_recall_comparison.png", dpi=160); plt.close(fig)

    threshold = pd.read_csv(results / "threshold_curve.csv")
    fig, ax = plt.subplots(figsize=(8.8, 5.2))
    ax.plot(threshold["threshold"], threshold["expected_cost_train_oof"], color=BLUE, linewidth=1.8)
    chosen = float(model["decision_threshold"])
    chosen_cost = float(threshold.loc[np.isclose(threshold["threshold"], chosen), "expected_cost_train_oof"].iloc[0])
    ax.scatter([chosen], [chosen_cost], color=GOLD, s=42, zorder=3, label=f"Seuil choisi {chosen:.3f}")
    ax.set_title("Coût pondéré sur prédictions hors pli du train")
    ax.set_xlabel("Seuil de probabilité")
    ax.set_ylabel("Coût estimé (unités du dataset)")
    ax.legend(frameon=False)
    style_axis(ax); fig.tight_layout(); fig.savefig(visuals / "cost_by_threshold.png", dpi=160); plt.close(fig)

    pivot = sensitivity.pivot(index="loss_severity_assumption", columns="legitimate_friction_cost_assumption", values="test_expected_cost_estimate")
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    image = ax.imshow(pivot.to_numpy(), cmap="Blues", aspect="auto")
    ax.set_xticks(np.arange(len(pivot.columns)), [f"{x:g}" for x in pivot.columns])
    ax.set_yticks(np.arange(len(pivot.index)), [f"{x:.0%}" for x in pivot.index])
    ax.set_xlabel("Friction par transaction légitime signalée")
    ax.set_ylabel("Sévérité supposée d'une fraude manquée")
    ax.set_title("Sensibilité du coût test estimé (unités dataset)")
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            ax.text(j, i, f"{pivot.iloc[i, j]:,.0f}", ha="center", va="center", color="black", fontsize=9)
    fig.colorbar(image, ax=ax, shrink=0.82, label="Coût estimé")
    fig.tight_layout(); fig.savefig(visuals / "cost_sensitivity.png", dpi=160); plt.close(fig)

    money = money.reset_index()
    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    x = np.arange(len(money))
    width = 0.24
    ax.bar(x - width, money["fraud_amount_intercepted_estimate"], width, label="Fraude interceptée (exposition)", color=BLUE)
    ax.bar(x, money["fraud_amount_missed_estimate"], width, label="Fraude manquée (exposition)", color=GOLD)
    ax.bar(x + width, money["legitimate_amount_blocked_estimate"], width, label="Montant légitime signalé", color=GRAY)
    ax.set_xticks(x, money["method"])
    ax.set_ylabel("Montant estimé; unité de la source")
    ax.set_title("Exposition détectée, manquée et friction")
    ax.legend(frameon=False, fontsize=8)
    style_axis(ax); fig.tight_layout(); fig.savefig(visuals / "exposure_intercepted_vs_missed.png", dpi=160); plt.close(fig)

    print(f"Fiche de score prête : 2 stratégies comparées, {len(sensitivity)} scénarios coût-friction, {len(recommendations)} recommandations.")
    print(f"Seuil recommandé {chosen:.3f}; coût test modèle {model_cost:,.0f} contre règle montant {baseline_cost:,.0f} unités du dataset.")


if __name__ == "__main__":
    main()
