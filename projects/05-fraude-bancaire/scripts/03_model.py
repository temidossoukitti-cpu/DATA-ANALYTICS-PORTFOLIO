"""Compare une règle métier simple à une régression logistique pondérée."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedGroupKFold

from pipeline_utils import (
    MODEL_FEATURES, ROOT, calibrate_population_weights, load_sample,
    make_duplicate_groups, new_logistic_pipeline, stratified_group_split,
    weighted_cost, weighted_quantile,
)

LOSS_SEVERITIES = [0.5, 1.0, 1.5]
FRICTION_COSTS = [5.0, 10.0, 25.0]
BASE_SEVERITY = 1.0
BASE_FRICTION = 10.0


def fit_oof_probabilities(train: pd.DataFrame, groups: np.ndarray) -> np.ndarray:
    y = train["Class"].to_numpy(dtype=int)
    x = train[MODEL_FEATURES].to_numpy(dtype=float)
    sample_weight = train["sampling_weight"].to_numpy(dtype=float)
    probabilities = np.full(len(train), np.nan, dtype=float)
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    for fit_index, valid_index in splitter.split(x, y, groups):
        estimator = new_logistic_pipeline()
        estimator.fit(x[fit_index], y[fit_index], logisticregression__sample_weight=sample_weight[fit_index])
        probabilities[valid_index] = estimator.predict_proba(x[valid_index])[:, 1]
    if not np.isfinite(probabilities).all():
        raise RuntimeError("La validation croisée n'a pas produit toutes les prédictions hors pli.")
    return probabilities


def threshold_cost_table(probabilities, y, amount, design_weights, severity, friction):
    eval_weights = calibrate_population_weights(y, design_weights)
    thresholds = np.arange(0.0, 1.0001, 0.001)
    rows = []
    for threshold in thresholds:
        predicted = (probabilities >= threshold).astype(int)
        cost = weighted_cost(y, predicted, amount, eval_weights, severity, friction)
        rows.append({"threshold": float(threshold), "expected_cost_train_oof": cost,
                     "weighted_precision": precision_score(y, predicted, sample_weight=eval_weights, zero_division=0),
                     "weighted_recall": recall_score(y, predicted, sample_weight=eval_weights, zero_division=0),
                     "transactions_flagged_estimate": float(np.sum(eval_weights * predicted))})
    table = pd.DataFrame(rows).sort_values(["threshold"], kind="stable").reset_index(drop=True)
    min_cost = table["expected_cost_train_oof"].min()
    best_rows = table.loc[np.isclose(table["expected_cost_train_oof"], min_cost, rtol=1e-12, atol=1e-10)]
    selected = float(best_rows["threshold"].max())
    return table, selected


def evaluate_rule(name, y, predicted, score, amount, weights, threshold, amount_cutoff, test_fraction, train_split_folds):
    tp = (y == 1) & (predicted == 1)
    fp = (y == 0) & (predicted == 1)
    fn = (y == 1) & (predicted == 0)
    tn = (y == 0) & (predicted == 0)
    return {
        "method": name,
        "decision_threshold": threshold,
        "amount_cutoff": amount_cutoff,
        "pr_auc_weighted": average_precision_score(y, score, sample_weight=weights),
        "precision_weighted": precision_score(y, predicted, sample_weight=weights, zero_division=0),
        "recall_weighted": recall_score(y, predicted, sample_weight=weights, zero_division=0),
        "f1_weighted": f1_score(y, predicted, sample_weight=weights, zero_division=0),
        "test_transactions_raw": int(len(y)),
        "test_transactions_population_estimate": float(weights.sum()),
        "test_fraction_of_sample": float(test_fraction),
        "train_stratified_group_folds_used_for_test": ",".join(str(i + 1) for i in train_split_folds),
        "tp_raw": int(tp.sum()), "fp_raw": int(fp.sum()), "fn_raw": int(fn.sum()), "tn_raw": int(tn.sum()),
        "tp_population_estimate": float(weights[tp].sum()),
        "fp_population_estimate": float(weights[fp].sum()),
        "fn_population_estimate": float(weights[fn].sum()),
        "tn_population_estimate": float(weights[tn].sum()),
        "score_definition": "Probabilité logistique pondérée" if name == "Modèle logistique" else "Montant Amount utilisé comme score de risque",
    }


def money_summary(name, y, predicted, amount, weights, severity=BASE_SEVERITY, friction=BASE_FRICTION):
    fraud = y == 1
    legitimate = y == 0
    missed = fraud & (predicted == 0)
    caught = fraud & (predicted == 1)
    false_positive = legitimate & (predicted == 1)
    flagged = predicted == 1
    return {
        "method": name,
        "transactions_flagged_estimate": float(weights[flagged].sum()),
        "legitimate_transactions_blocked_estimate": float(weights[false_positive].sum()),
        "fraud_transactions_intercepted_estimate": float(weights[caught].sum()),
        "fraud_transactions_missed_estimate": float(weights[missed].sum()),
        "amount_flagged_estimate": float(np.sum(weights[flagged] * amount[flagged])),
        "fraud_amount_intercepted_estimate": float(np.sum(weights[caught] * amount[caught])),
        "fraud_amount_missed_estimate": float(np.sum(weights[missed] * amount[missed])),
        "legitimate_amount_blocked_estimate": float(np.sum(weights[false_positive] * amount[false_positive])),
        "expected_cost_estimate": weighted_cost(y, predicted, amount, weights, severity, friction),
        "missed_fraud_loss_severity_assumption": severity,
        "legitimate_friction_cost_assumption": friction,
        "cost_unit": "dataset amount units; currency unspecified",
    }


def main() -> None:
    sample = load_sample().reset_index(drop=True)
    y_all = sample["Class"].to_numpy(dtype=int)
    groups = make_duplicate_groups(sample)
    train_index, test_index, selected_folds = stratified_group_split(y_all, groups, test_fraction=0.30, seed=42)
    train = sample.iloc[train_index].reset_index(drop=True)
    test = sample.iloc[test_index].reset_index(drop=True)
    train_groups = groups[train_index]
    x_train = train[MODEL_FEATURES].to_numpy(dtype=float)
    y_train = train["Class"].to_numpy(dtype=int)
    w_train = train["sampling_weight"].to_numpy(dtype=float)
    x_test = test[MODEL_FEATURES].to_numpy(dtype=float)
    y_test = test["Class"].to_numpy(dtype=int)
    amount_test = test["Amount"].to_numpy(dtype=float)
    w_test = calibrate_population_weights(y_test, test["sampling_weight"].to_numpy(dtype=float))
    test_fraction = len(test) / len(sample)

    # Pick the threshold on group-stratified out-of-fold training scores, never on test labels.
    oof_probability = fit_oof_probabilities(train, train_groups)
    oof_y = y_train
    oof_amount = train["Amount"].to_numpy(dtype=float)
    oof_design_weight = train["sampling_weight"].to_numpy(dtype=float)
    cost_tables = {}
    selected_thresholds = {}
    for severity in LOSS_SEVERITIES:
        for friction in FRICTION_COSTS:
            key = (severity, friction)
            table, threshold = threshold_cost_table(oof_probability, oof_y, oof_amount, oof_design_weight, severity, friction)
            cost_tables[key] = table
            selected_thresholds[key] = threshold
    threshold_curve = cost_tables[(BASE_SEVERITY, BASE_FRICTION)].copy()
    threshold_curve.to_csv(ROOT / "results/threshold_curve.csv", index=False, encoding="utf-8")
    recommended_threshold = selected_thresholds[(BASE_SEVERITY, BASE_FRICTION)]

    model = new_logistic_pipeline()
    model.fit(x_train, y_train, logisticregression__sample_weight=w_train)
    test_probability = model.predict_proba(x_test)[:, 1]
    model_prediction = (test_probability >= recommended_threshold).astype(int)

    # Business-rule baseline: monitor the top 1% of legitimate training amounts.
    train_legit = train.loc[train["Class"].eq(0)]
    amount_cutoff = weighted_quantile(train_legit["Amount"], 0.99, train_legit["sampling_weight"])
    baseline_prediction = (amount_test >= amount_cutoff).astype(int)
    baseline_score = amount_test

    metrics = [
        evaluate_rule("Modèle logistique", y_test, model_prediction, test_probability, amount_test, w_test,
                      recommended_threshold, np.nan, test_fraction, selected_folds),
        evaluate_rule("Règle montant P99", y_test, baseline_prediction, baseline_score, amount_test, w_test,
                      np.nan, amount_cutoff, test_fraction, selected_folds),
    ]
    metrics_frame = pd.DataFrame(metrics)
    metrics_frame.to_csv(ROOT / "results/model_metrics.csv", index=False, encoding="utf-8")

    money_rows = [
        money_summary("Modèle logistique", y_test, model_prediction, amount_test, w_test),
        money_summary("Règle montant P99", y_test, baseline_prediction, amount_test, w_test),
    ]
    pd.DataFrame(money_rows).to_csv(ROOT / "results/money_controls.csv", index=False, encoding="utf-8")

    sensitivity_rows = []
    for (severity, friction), train_table in cost_tables.items():
        threshold = selected_thresholds[(severity, friction)]
        predicted = (test_probability >= threshold).astype(int)
        result = money_summary("Modèle logistique", y_test, predicted, amount_test, w_test, severity, friction)
        sensitivity_rows.append({
            "loss_severity_assumption": severity,
            "legitimate_friction_cost_assumption": friction,
            "threshold_selected_on_training_oof": threshold,
            "test_expected_cost_estimate": result["expected_cost_estimate"],
            "test_weighted_precision": precision_score(y_test, predicted, sample_weight=w_test, zero_division=0),
            "test_weighted_recall": recall_score(y_test, predicted, sample_weight=w_test, zero_division=0),
            "test_fraud_amount_missed_estimate": result["fraud_amount_missed_estimate"],
            "test_legitimate_transactions_blocked_estimate": result["legitimate_transactions_blocked_estimate"],
            "cost_unit": "dataset amount units; currency unspecified",
        })
    sensitivity = pd.DataFrame(sensitivity_rows).sort_values(["loss_severity_assumption", "legitimate_friction_cost_assumption"])
    sensitivity.to_csv(ROOT / "results/cost_sensitivity.csv", index=False, encoding="utf-8")

    # Keep all source rows in the star fact; mark only held-out observations as scored.
    partition = np.full(len(sample), "train", dtype=object)
    partition[test_index] = "test"
    fact = pd.read_csv(ROOT / "data/processed/fact_transactions.csv")
    fact["sample_partition"] = partition
    fact.to_csv(ROOT / "data/processed/fact_transactions.csv", index=False, encoding="utf-8")
    split_groups = pd.DataFrame({"duplicate_group": groups, "partition": partition})
    crossing_groups = int(split_groups.groupby("duplicate_group")["partition"].nunique().gt(1).sum())
    split_checks = [
        {"metric": "sample_rows", "value": len(sample), "unit": "rows", "status": "PASS", "definition": "Échantillon évalué."},
        {"metric": "train_rows", "value": len(train), "unit": "rows", "status": "PASS", "definition": "Lignes train du split group-stratifié."},
        {"metric": "test_rows", "value": len(test), "unit": "rows", "status": "PASS", "definition": "Lignes test du split group-stratifié."},
        {"metric": "test_fraction", "value": test_fraction, "unit": "proportion", "status": "PASS" if abs(test_fraction - 0.30) <= 0.005 else "FAIL", "definition": "Proportion test visée 30 %."},
        {"metric": "fraud_train_rows", "value": int(y_train.sum()), "unit": "rows", "status": "PASS" if y_train.sum() > 0 else "FAIL", "definition": "Fraudes étiquetées en train."},
        {"metric": "fraud_test_rows", "value": int(y_test.sum()), "unit": "rows", "status": "PASS" if y_test.sum() > 0 else "FAIL", "definition": "Fraudes étiquetées en test."},
        {"metric": "duplicate_groups_crossing_partitions", "value": crossing_groups, "unit": "groups", "status": "PASS" if crossing_groups == 0 else "FAIL", "definition": "Groupes d'attributs identiques présents à la fois en train et en test; attendu 0."},
        {"metric": "selected_test_folds", "value": ";".join(str(i + 1) for i in selected_folds), "unit": "folds", "status": "PASS", "definition": "Trois plis de StratifiedGroupKFold affectés au test."},
        {"metric": "threshold_selection", "value": "training_oof", "unit": "source", "status": "PASS", "definition": "Le seuil est choisi sur des prédictions hors pli du train, jamais sur les étiquettes test."},
        {"metric": "random_state", "value": 42, "unit": "seed", "status": "PASS", "definition": "Graine du split group-stratifié et de la validation croisée."},
    ]
    pd.DataFrame(split_checks).to_csv(ROOT / "results/split_validation.csv", index=False, encoding="utf-8")

    test_fact = test[["transaction_id", "Amount", "Class", "sampling_weight", "Time"]].copy()
    test_fact["model_probability"] = test_probability
    test_fact["model_prediction"] = model_prediction
    test_fact["baseline_amount_flag"] = baseline_prediction
    test_fact["eval_population_weight"] = w_test
    test_fact["loss_severity_assumption"] = BASE_SEVERITY
    test_fact["legitimate_friction_cost_assumption"] = BASE_FRICTION
    test_fact["expected_cost_contribution"] = np.where(
        (y_test == 1) & (model_prediction == 0), amount_test * BASE_SEVERITY * w_test,
        np.where((y_test == 0) & (model_prediction == 1), BASE_FRICTION * w_test, 0.0),
    )
    test_fact["fraud_amount_missed_contribution"] = np.where((y_test == 1) & (model_prediction == 0), amount_test * w_test, 0.0)
    test_fact["fraud_amount_intercepted_contribution"] = np.where((y_test == 1) & (model_prediction == 1), amount_test * w_test, 0.0)
    test_fact["legitimate_amount_blocked_contribution"] = np.where((y_test == 0) & (model_prediction == 1), amount_test * w_test, 0.0)
    test_fact = test_fact.rename(columns={"Amount": "amount", "Class": "outcome_key", "Time": "time_seconds"})
    test_fact["amount_band_key"] = np.select([test_fact["amount"].le(10), test_fact["amount"].le(50), test_fact["amount"].le(200)], [1, 2, 3], default=4).astype(int)
    test_fact["time_window_key"] = np.minimum((test_fact["time_seconds"] // 21600).astype(int) + 1, 8)
    test_fact.to_csv(ROOT / "data/processed/fact_model_test.csv", index=False, encoding="utf-8", float_format="%.10f")

    scorecard = pd.DataFrame([{
        "model_name": "Régression logistique pondérée",
        "recommended_threshold": recommended_threshold,
        "pr_auc_test": metrics[0]["pr_auc_weighted"],
        "precision_test": metrics[0]["precision_weighted"],
        "recall_test": metrics[0]["recall_weighted"],
        "f1_test": metrics[0]["f1_weighted"],
        "expected_cost_test": money_rows[0]["expected_cost_estimate"],
        "test_transactions_population_estimate": metrics[0]["test_transactions_population_estimate"],
        "split_method": "StratifiedGroupKFold 10 plis, 3 plis test; groupes de doublons non séparés; seed 42",
        "features_used": "V1–V28, Amount; Time excluded",
    }])
    scorecard.to_csv(ROOT / "data/processed/model_scorecard.csv", index=False, encoding="utf-8")

    print(f"Split groupé stratifié: train={len(train):,} ({1-test_fraction:.2%}); test={len(test):,} ({test_fraction:.2%}); doublons non séparés.")
    print(f"Fraudes train/test: {int(y_train.sum())}/{int(y_test.sum())}; seuil choisi hors test={recommended_threshold:.3f}; règle montant P99={amount_cutoff:.2f} unités.")
    print(f"Modèle test pondéré: PR-AUC={metrics[0]['pr_auc_weighted']:.4f}; précision={metrics[0]['precision_weighted']:.4f}; rappel={metrics[0]['recall_weighted']:.4f}; coût estimé={money_rows[0]['expected_cost_estimate']:.2f} unités.")


if __name__ == "__main__":
    main()
