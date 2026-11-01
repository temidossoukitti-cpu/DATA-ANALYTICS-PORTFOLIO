"""Construction du modèle logistique, évaluation et livrables."""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (precision_recall_curve, auc as pr_auc, roc_curve, roc_auc_score,
                             f1_score, precision_score, recall_score, accuracy_score)
from sklearn.model_selection import StratifiedGroupKFold

from pipeline_utils import (
    ROOT, build_model, metrics_at_threshold, fr_num, fr_pct,
    stratified_group_split, make_groups, CATEGORICAL_FEATURES, NUMERIC_FEATURES,
    MODEL_FEATURES, SEED,
)


def main() -> None:
    fact = pd.read_csv(ROOT / "data/processed/fact_campaign.csv")
    # Séparation train / test group-stratifié 70/30
    model_columns = [
        "age", "campaign", "pdays", "previous", "emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed",
        "job_key", "marital_key", "education_key", "default_status", "housing_loan", "personal_loan", "contact_key", "month_key", "day_of_week", "poutcome_key",
    ]
    X = fact[model_columns].copy()
    y = fact["outcome_key"].values
    groups = make_groups(fact)
    train_idx, test_idx, selected_folds = stratified_group_split(y, groups, test_fraction=0.30)

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    # Modèle entraîné sur l'ensemble d'entraînement
    model = build_model()
    model.fit(X_train, y_train)

    # Probabilités sur le test
    proba_test = model.predict_proba(X_test)[:, 1]

    # Sélection du seuil sur les prédictions hors pli (OOF) via 5-fold StratifiedGroupKFold
    oof = np.zeros(len(X_train))
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    groups_train = groups.iloc[train_idx] if isinstance(groups, pd.Series) else groups[train_idx]
    for fold, (train, valid) in enumerate(sgkf.split(X_train, y_train, groups_train)):
        m = build_model()
        m.fit(X_train.iloc[train], y_train[train])
        oof[valid] = m.predict_proba(X_train.iloc[valid])[:, 1]

    # Grid de seuils et choix maximisant F1 sur OOF
    thresholds = np.arange(0.05, 0.96, 0.01)
    best_f1 = -1.0
    best_threshold = 0.5
    for t in thresholds:
        metrics = metrics_at_threshold(y_train, oof, t)
        if metrics["f1"] > best_f1:
            best_f1 = metrics["f1"]
            best_threshold = t

    # Métriques sur le test avec le seuil choisi
    test_metrics = metrics_at_threshold(y_test, proba_test, best_threshold)

    # Modèle basique : poutcome == success sur test
    baseline_rule_pred = (fact.loc[test_idx, "poutcome_key"] == 3).astype(int).values
    baseline_metrics = metrics_at_threshold(y_test, baseline_rule_pred.astype(float), 0.5)

    # Lift par décile (sur test)
    lift_df = pd.DataFrame({
        "proba": proba_test,
        "y_true": y_test,
    })
    lift_df = lift_df.sort_values("proba", ascending=False).reset_index(drop=True)
    # Déciles par rangs (10 groupes égaux)
    lift_df["decile"] = pd.cut(lift_df.index, bins=10, labels=range(1, 11)).astype(int)
    decile_stats = (
        lift_df.groupby("decile")
        .agg(n_rows=("y_true", "count"), n_subs=("y_true", "sum"))
        .reset_index()
    )
    decile_stats["conversion_rate"] = decile_stats["n_subs"] / decile_stats["n_rows"]
    base_rate = y_test.mean()
    decile_stats["lift"] = decile_stats["conversion_rate"] / base_rate
    lift_df.to_csv(ROOT / "results/lift_table.csv", index=False, encoding="utf-8")
    decile_stats.to_csv(ROOT / "results/decile_stats.csv", index=False, encoding="utf-8")

    # Courbe PR
    prec, rec, thr = precision_recall_curve(y_test, proba_test)
    pr_auc_val = pr_auc(rec, prec)
    roc_auc = roc_auc_score(y_test, proba_test)

    # Courbe seuil
    threshold_vals = np.arange(0.05, 0.96, 0.01)
    thr_prec, thr_rec, thr_f1 = [], [], []
    for t in threshold_vals:
        m = metrics_at_threshold(y_test, proba_test, t)
        thr_prec.append(m["precision"]); thr_rec.append(m["recall"]); thr_f1.append(m["f1"])
    thr_curve = pd.DataFrame({
        "threshold": threshold_vals, "precision": thr_prec, "recall": thr_rec, "f1": thr_f1,
    })
    thr_curve.to_csv(ROOT / "results/threshold_curve.csv", index=False, encoding="utf-8")

    # Distribution des probabilités
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    legit = proba_test[y_test == 0]
    fraude = proba_test[y_test == 1]
    ax.hist(legit, bins=40, alpha=0.5, label="Légitime", density=True, color="#7b8794")
    ax.hist(fraude, bins=40, alpha=0.5, label="Souscrit", density=True, color="#c69214")
    ax.set_title("Distribution des probabilités du modèle (échantillon test)")
    ax.set_xlabel("Probabilité de souscription")
    ax.set_ylabel("Densité pondérée")
    ax.legend(frameon=False)
    style_axis(ax); fig.tight_layout(); fig.savefig(ROOT / "visuals/probability_distribution.png", dpi=160); plt.close(fig)

    # Courbe PR
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.plot(rec, prec, label=f"PR curve (AUC={pr_auc_val:.4f})")
    ax.set_title("Courbe Précision-Rappel")
    ax.set_xlabel("Rappel")
    ax.set_ylabel("Précision")
    ax.legend(frameon=False)
    style_axis(ax); fig.tight_layout(); fig.savefig(ROOT / "visuals/precision_recall_curve.png", dpi=160); plt.close(fig)

    # Courbe seuil vs F1
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.plot(threshold_vals, thr_f1, label="F1")
    ax.set_title("F1 selon le seuil choisi")
    ax.set_xlabel("Seuil de probabilité")
    ax.set_ylabel("F1")
    ax.legend(frameon=False)
    style_axis(ax); fig.tight_layout(); fig.savefig(ROOT / "results/threshold_vs_f1.png", dpi=160); plt.close(fig)

    # Tableau récapitulatif des métriques
    model_scorecard = pd.DataFrame([{
        "model_name": "Modèle logistique",
        "recommended_threshold": best_threshold,
        "roc_auc_test": roc_auc,
        "pr_auc_test": pr_auc_val,
        "precision_test": test_metrics["precision"],
        "recall_test": test_metrics["recall"],
        "f1_test": test_metrics["f1"],
        "accuracy_test": test_metrics["accuracy"],
        "test_rows": int(len(y_test)),
        "positives_test": int(y_test.sum()),
        "features_used": ", ".join(MODEL_FEATURES),
        "split_method": "StratifiedGroupKFold 70/30; seuil optimisant F1 sur OOF 5-fold",
    }])
    model_scorecard.to_csv(ROOT / "results/model_scorecard.csv", index=False, encoding="utf-8")

    # Métriques agrégées
    model_metrics = pd.DataFrame([{
        "method": "Modèle logistique",
        "precision_weighted": test_metrics["precision"],
        "recall_weighted": test_metrics["recall"],
        "f1_weighted": test_metrics["f1"],
        "accuracy": test_metrics["accuracy"],
        "threshold_selected": best_threshold,
        "pr_auc": pr_auc_val,
        "roc_auc": roc_auc,
    }])
    model_metrics.to_csv(ROOT / "results/model_metrics.csv", index=False, encoding="utf-8")

    # Comparaison modèle vs règle poutcome=success
    baseline_metrics_df = pd.DataFrame([{
        "method": "Règle poutcome=success",
        "precision_weighted": baseline_metrics["precision"],
        "recall_weighted": baseline_metrics["recall"],
        "f1_weighted": baseline_metrics["f1"],
        "accuracy": baseline_metrics["accuracy"],
        "threshold_selected": "N/A (taux naturel)",
        "pr_auc": "N/A",
        "roc_auc": "N/A",
    }])
    baseline_metrics_df.to_csv(ROOT / "results/metrics_baseline.csv", index=False, encoding="utf-8")

    # Split validation
    duplicate_groups_crossing = int(((fact.iloc[train_idx].duplicated(subset=model_columns).sum()) +
                                     (fact.iloc[test_idx].duplicated(subset=model_columns).sum())))
    split_validation = pd.DataFrame([{
        "test_fraction_observed": float(len(test_idx) / len(y)),
        "test_fraction_target": 0.30,
        "diff_fraction": abs(float(len(test_idx) / len(y)) - 0.30),
        "duplicate_groups_crossing": duplicate_groups_crossing,
        "selected_folds": str(selected_folds),
        "class_balance_train": f"{float(y[train_idx].sum()) / len(train_idx):.4%}",
        "class_balance_test": f"{float(y_test.sum()) / len(test_idx):.4%}",
    }])
    split_validation.to_csv(ROOT / "results/split_validation.csv", index=False, encoding="utf-8")

    # overall KPIs update
    subscriptions = int(fact["outcome_key"].sum())
    overall_rows = [
        {"metric": "campaign_rows", "value": len(fact), "unit": "campaigns", "source": "results/overall_kpis.csv"},
        {"metric": "subscriptions", "value": subscriptions, "unit": "subscriptions", "source": "results/overall_kpis.csv"},
        {"metric": "conversion_rate", "value": subscriptions / len(fact), "unit": "proportion", "source": "results/overall_kpis.csv"},
    ]
    overall = pd.DataFrame(overall_rows)
    overall.to_csv(ROOT / "results/overall_kpis.csv", index=False, encoding="utf-8")

    print(f"Modèle entraîné : F1 test={test_metrics['f1']:.4f}, seuil={best_threshold:.3f}, PR-AUC={pr_auc_val:.4f}, ROC-AUC={roc_auc:.4f}.")
    print(f"Baseline règle poutcome=success : précision {baseline_metrics['precision']:.4f}, rappel {baseline_metrics['recall']:.4f}, F1 {baseline_metrics['f1']:.4f}.")
    print(f"Lift table et déciles écrits.")


def style_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.2, linewidth=0.7)
    ax.set_axisbelow(True)


if __name__ == "__main__":
    main()
