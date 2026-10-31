"""Scoring logistique 70/30, résultats hors échantillon et analyses de risque."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from pipeline_utils import PROCESSED_DIR, RESULTS_DIR, RISK_BANDS, VISUALS_DIR, write_csv

RANDOM_STATE = 42
TEST_SIZE = 0.30
DECISION_THRESHOLD = 0.25
BASE_LGD = 0.45
LGD_SENSITIVITY = [0.30, 0.45, 0.60]
NUMERIC_FEATURES = [
    "limit_bal",
    "pay_0", "pay_2", "pay_3", "pay_4", "pay_5", "pay_6",
    "bill_amt1", "bill_amt2", "bill_amt3", "bill_amt4", "bill_amt5", "bill_amt6",
    "pay_amt1", "pay_amt2", "pay_amt3", "pay_amt4", "pay_amt5", "pay_amt6",
    "utilization", "payment_ratio_m1", "max_delay_6m", "n_delays_6m", "risk_flag_recent_delay",
]
CATEGORICAL_FEATURES = ["education"]
FORBIDDEN_FEATURES = {"client_id", "sex", "marriage", "age", "education_original", "marriage_original"}


def assign_risk_band(probability: pd.Series) -> pd.Series:
    return pd.Series(
        np.select(
            [probability < 0.10, probability < 0.20, probability < 0.40],
            [1, 2, 3],
            default=4,
        ),
        index=probability.index,
        dtype="int64",
    )


def expected_loss(probability: pd.Series, bill_amount: pd.Series, lgd: float) -> pd.Series:
    """Perte attendue illustrée: PD × facture positive × LGD supposée."""
    exposure = bill_amount.clip(lower=0).fillna(0)
    return probability.fillna(0) * exposure * lgd


def set_plot_style() -> None:
    plt.style.use("default")
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.22,
            "grid.linestyle": "--",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def main() -> None:
    frame = pd.read_csv(PROCESSED_DIR / "fact_clients.csv")
    features = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    if set(features) & FORBIDDEN_FEATURES:
        raise ValueError("Une variable protégée ou un identifiant est inclus dans les prédicteurs.")
    if not set(features).issubset(frame.columns):
        raise ValueError("Une ou plusieurs variables de score sont absentes du fait traité.")

    train_ids, test_ids = train_test_split(
        frame["client_id"],
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=frame["default_next_month"],
    )
    train_mask = frame["client_id"].isin(train_ids)
    test_mask = frame["client_id"].isin(test_ids)
    X_train = frame.loc[train_mask, features]
    y_train = frame.loc[train_mask, "default_next_month"].astype("int64")
    X_test = frame.loc[test_mask, features]
    y_test = frame.loc[test_mask, "default_next_month"].astype("int64")

    numeric_pipeline = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median")), ("standardizer", StandardScaler())]
    )
    categorical_pipeline = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="most_frequent")), ("encoder", OneHotEncoder(handle_unknown="ignore"))]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("education", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("logistic", LogisticRegression(max_iter=2000, random_state=RANDOM_STATE, solver="lbfgs")),
        ]
    )
    model.fit(X_train, y_train)

    all_probabilities = pd.Series(model.predict_proba(frame[features])[:, 1], index=frame.index)
    all_bands = assign_risk_band(all_probabilities)
    frame["predicted_pd"] = all_probabilities
    frame["risk_band_key"] = all_bands
    frame["model_partition"] = np.where(test_mask, "Test", "Train")
    write_csv(frame, PROCESSED_DIR / "fact_clients.csv")

    test = frame.loc[test_mask].copy()
    y_probability = test["predicted_pd"].astype(float)
    y_true = test["default_next_month"].astype("int64")
    y_class = (y_probability >= DECISION_THRESHOLD).astype("int64")
    fpr, tpr, roc_thresholds = roc_curve(y_true, y_probability)
    ks = float(np.max(tpr - fpr))
    tn, fp, fn, tp = confusion_matrix(y_true, y_class, labels=[0, 1]).ravel()
    metrics = pd.DataFrame(
        [
            {
                "random_state": RANDOM_STATE,
                "train_fraction": 1.0 - TEST_SIZE,
                "test_fraction": TEST_SIZE,
                "train_clients": int(train_mask.sum()),
                "test_clients": int(test_mask.sum()),
                "test_default_rate": float(y_true.mean()),
                "decision_threshold": DECISION_THRESHOLD,
                "roc_auc": float(roc_auc_score(y_true, y_probability)),
                "pr_auc_average_precision": float(average_precision_score(y_true, y_probability)),
                "ks_statistic": ks,
                "precision_at_threshold": float(precision_score(y_true, y_class, zero_division=0)),
                "recall_at_threshold": float(recall_score(y_true, y_class, zero_division=0)),
                "brier_score": float(brier_score_loss(y_true, y_probability)),
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp),
                "base_lgd_assumption": BASE_LGD,
                "risk_band_cutoffs": "<0.10; 0.10-<0.20; 0.20-<0.40; >=0.40",
                "protected_features_excluded": "sex; marriage; age",
            }
        ]
    )
    write_csv(metrics, RESULTS_DIR / "model_metrics.csv")

    risk_dimension = pd.read_csv(PROCESSED_DIR / "dim_risk_band.csv")
    label_map = risk_dimension.set_index("risk_band_key")["risk_band_label"].to_dict()
    test["risk_band_label"] = test["risk_band_key"].map(label_map)
    test["positive_bill_exposure"] = test["bill_amt1"].clip(lower=0)
    test["expected_loss_lgd45_ntd"] = expected_loss(test["predicted_pd"], test["bill_amt1"], BASE_LGD)
    total_test_bill_exposure = float(test["positive_bill_exposure"].sum())
    band_summary = test.groupby("risk_band_key", observed=True).agg(
        customers=("client_id", "size"),
        default_count=("default_next_month", "sum"),
        default_rate=("default_next_month", "mean"),
        average_predicted_pd=("predicted_pd", "mean"),
        total_credit_limit_ntd=("limit_bal", "sum"),
        defaulter_credit_limit_exposure_ntd=("limit_bal", lambda values: float(values[test.loc[values.index, "default_next_month"].eq(1)].sum())),
        positive_bill_exposure_ntd=("positive_bill_exposure", "sum"),
        expected_loss_lgd45_ntd=("expected_loss_lgd45_ntd", "sum"),
    ).reindex([1, 2, 3, 4]).reset_index()
    band_summary["risk_band_label"] = band_summary["risk_band_key"].map(label_map)
    band_summary["share_test_bill_exposure"] = band_summary["positive_bill_exposure_ntd"] / total_test_bill_exposure
    write_csv(band_summary, RESULTS_DIR / "risk_band_summary.csv")

    sensitivity_rows = []
    for _, row in test.iterrows():
        for lgd in LGD_SENSITIVITY:
            sensitivity_rows.append(
                {
                    "risk_band_key": int(row["risk_band_key"]),
                    "risk_band_label": row["risk_band_label"],
                    "lgd_assumption": lgd,
                    "expected_loss_ntd": float(expected_loss(pd.Series([row["predicted_pd"]]), pd.Series([row["bill_amt1"]]), lgd).iloc[0]),
                }
            )
    sensitivity = pd.DataFrame(sensitivity_rows).groupby(
        ["risk_band_key", "risk_band_label", "lgd_assumption"], as_index=False
    )["expected_loss_ntd"].sum()
    write_csv(sensitivity, RESULTS_DIR / "expected_loss_sensitivity.csv")

    test_export = test[
        ["client_id", "default_next_month", "predicted_pd", "risk_band_key", "risk_band_label", "limit_bal", "bill_amt1", "model_partition"]
    ].copy()
    write_csv(test_export, RESULTS_DIR / "test_predictions.csv")

    ordered = test.sort_values("predicted_pd", ascending=False).copy()
    ordered["rank_from_highest_score"] = ordered["predicted_pd"].rank(method="first", ascending=False)
    ordered["decile"] = pd.qcut(ordered["rank_from_highest_score"], q=10, labels=False).astype("int64") + 1
    baseline_rate = float(y_true.mean())
    deciles = ordered.groupby("decile", observed=True).agg(
        customers=("client_id", "size"),
        default_count=("default_next_month", "sum"),
        default_rate=("default_next_month", "mean"),
        average_predicted_pd=("predicted_pd", "mean"),
        positive_bill_exposure_ntd=("bill_amt1", lambda values: float(values.clip(lower=0).sum())),
    ).reset_index()
    deciles["lift_vs_test_baseline"] = deciles["default_rate"] / baseline_rate
    write_csv(deciles, RESULTS_DIR / "decile_lift.csv")

    calibration = test.copy()
    calibration["rank_from_lowest_score"] = calibration["predicted_pd"].rank(method="first", ascending=True)
    calibration["calibration_bin"] = pd.qcut(calibration["rank_from_lowest_score"], q=10, labels=False).astype("int64") + 1
    calibration_bins = calibration.groupby("calibration_bin", observed=True).agg(
        customers=("client_id", "size"),
        mean_predicted_pd=("predicted_pd", "mean"),
        observed_default_rate=("default_next_month", "mean"),
    ).reset_index()
    calibration_bins["calibration_gap"] = calibration_bins["observed_default_rate"] - calibration_bins["mean_predicted_pd"]
    write_csv(calibration_bins, RESULTS_DIR / "calibration_bins.csv")

    transformed_names = model.named_steps["preprocessor"].get_feature_names_out()
    coefficients = pd.DataFrame(
        {
            "feature": transformed_names,
            "coefficient": model.named_steps["logistic"].coef_[0],
        }
    )
    coefficients["odds_ratio_per_scaled_unit"] = np.exp(coefficients["coefficient"])
    coefficients["absolute_coefficient"] = coefficients["coefficient"].abs()
    coefficients = coefficients.sort_values("absolute_coefficient", ascending=False)
    write_csv(coefficients, RESULTS_DIR / "model_coefficients.csv")

    recent = frame[frame["risk_flag_recent_delay"] == 1]
    high_util_recent = frame[(frame["utilization"] >= 0.60) & (frame["risk_flag_recent_delay"] == 1)]
    very_high = test[test["risk_band_key"] == 4]
    high_rate_limit = pd.read_csv(RESULTS_DIR / "default_by_segment.csv")
    high_rate_limit = high_rate_limit.loc[
        (high_rate_limit["segment_type"] == "Limite de crédit") & (high_rate_limit["customers"] >= 100)
    ].sort_values(["default_rate", "customers"], ascending=[False, False])
    if high_rate_limit.empty:
        limit_action_segment = "Aucun segment de limite avec au moins 100 clients"
        limit_action = pd.DataFrame()
        limit_exposure = 0.0
    else:
        limit_action = high_rate_limit.iloc[0]
        limit_action_segment = str(limit_action["segment"])
        limit_exposure = float(limit_action["defaulter_limit_exposure"])
    recommendations = pd.DataFrame(
        [
            {
                "recommendation_id": "R1",
                "trigger": "pay_0 >= 1",
                "cohort_customers": int(len(recent)),
                "observed_default_rate": float(recent["default_next_month"].mean()) if len(recent) else np.nan,
                "exposure_ntd": float(recent.loc[recent["default_next_month"] == 1, "limit_bal"].sum()),
                "expected_loss_ntd": np.nan,
                "action": "Déclencher une revue de recouvrement dès l’apparition d’un retard récent; vérifier la capacité opérationnelle avant toute généralisation.",
                "evidence": "results/default_by_segment.csv; results/default_rate_by_pay0.csv",
            },
            {
                "recommendation_id": "R2",
                "trigger": "utilization >= 0.60 et pay_0 >= 1",
                "cohort_customers": int(len(high_util_recent)),
                "observed_default_rate": float(high_util_recent["default_next_month"].mean()) if len(high_util_recent) else np.nan,
                "exposure_ntd": float(high_util_recent.loc[high_util_recent["default_next_month"] == 1, "limit_bal"].sum()),
                "expected_loss_ntd": np.nan,
                "action": "Soumettre les demandes de hausse de limite à une revue manuelle pour ce segment; ne pas bloquer automatiquement les clients.",
                "evidence": "results/default_by_segment.csv; results/quality_check.csv",
            },
            {
                "recommendation_id": "R3",
                "trigger": "Bande très élevée, PD >= 0.40, partition test",
                "cohort_customers": int(len(very_high)),
                "observed_default_rate": float(very_high["default_next_month"].mean()) if len(very_high) else np.nan,
                "exposure_ntd": float(very_high.loc[very_high["default_next_month"] == 1, "limit_bal"].sum()),
                "expected_loss_ntd": float(expected_loss(very_high["predicted_pd"], very_high["bill_amt1"], BASE_LGD).sum()),
                "action": "Prioriser ces dossiers pour une revue humaine et une relance adaptée; seuils de bandes considérés comme hypothèses de triage.",
                "evidence": "results/risk_band_summary.csv; results/expected_loss_sensitivity.csv",
            },
            {
                "recommendation_id": "R4",
                "trigger": f"Bande de limite {limit_action_segment}, partition complète",
                "cohort_customers": int(limit_action["customers"]) if not limit_action.empty else 0,
                "observed_default_rate": float(limit_action["default_rate"]) if not limit_action.empty else np.nan,
                "exposure_ntd": limit_exposure,
                "expected_loss_ntd": np.nan,
                "action": "Examiner la politique de limite et la composition de cette bande avant toute modification; le taux observé ne démontre pas un effet causal.",
                "evidence": "results/default_by_segment.csv",
            },
        ]
    )
    write_csv(recommendations, RESULTS_DIR / "recommendations.csv")

    set_plot_style()
    VISUALS_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    band_plot = band_summary.sort_values("risk_band_key")
    ax.bar(band_plot["risk_band_label"], band_plot["defaulter_credit_limit_exposure_ntd"] / 1_000_000, color="#647D8E")
    ax.set_title("Limites détenues par les défaillants, par bande de score test")
    ax.set_ylabel("Exposition en millions de NT$")
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(VISUALS_DIR / "exposure_by_risk_band.png", dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 5.2))
    ax.plot(fpr, tpr, color="#526D82", linewidth=2, label=f"ROC-AUC = {metrics.loc[0, 'roc_auc']:.3f}")
    ax.plot([0, 1], [0, 1], color="#A7A7A7", linestyle="--", label="Référence aléatoire")
    ax.set_title("Courbe ROC sur la partition test")
    ax.set_xlabel("Taux de faux positifs")
    ax.set_ylabel("Taux de vrais positifs")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(VISUALS_DIR / "roc_curve.png", dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.bar(deciles["decile"].astype(str), deciles["lift_vs_test_baseline"], color="#7C8F9A")
    ax.axhline(1.0, color="#666666", linestyle="--", linewidth=1)
    ax.set_title("Lift par décile de probabilité, partition test")
    ax.set_xlabel("Décile (le premier est le score le plus élevé)")
    ax.set_ylabel("Lift par rapport au taux test")
    fig.tight_layout()
    fig.savefig(VISUALS_DIR / "lift_by_decile.png", dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    expected_chart = band_summary.sort_values("risk_band_key")
    ax.bar(expected_chart["risk_band_label"], expected_chart["expected_loss_lgd45_ntd"] / 1_000_000, color="#718A9A")
    ax.set_title("Perte attendue par bande de risque, LGD supposée à 45 %")
    ax.set_ylabel("Perte attendue en millions de NT$")
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(VISUALS_DIR / "expected_loss_by_band.png", dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(
        f"Modèle terminé : ROC-AUC test={metrics.loc[0, 'roc_auc']:.4f}; "
        f"PR-AUC={metrics.loc[0, 'pr_auc_average_precision']:.4f}; KS={ks:.4f}; "
        f"seuil={DECISION_THRESHOLD:.2f}."
    )


if __name__ == "__main__":
    main()
