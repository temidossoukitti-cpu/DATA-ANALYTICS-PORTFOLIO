"""Analyse descriptive et graphiques du projet 04."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pipeline_utils import PROCESSED_DIR, RESULTS_DIR, VISUALS_DIR, default_rate, write_csv


def segment_statistics(frame: pd.DataFrame, column: str, segment_name: str) -> pd.DataFrame:
    working = frame.copy()
    working["segment"] = working[column].astype("string").fillna("Non renseigné")
    working["defaulter_limit_exposure"] = working["limit_bal"].where(working["default_next_month"] == 1, 0)
    working["defaulter_bill_exposure"] = working["bill_amt1"].clip(lower=0).where(working["default_next_month"] == 1, 0)
    grouped = working.groupby("segment", observed=True, dropna=False)
    result = grouped.agg(
        customers=("client_id", "size"),
        default_count=("default_next_month", "sum"),
        default_rate=("default_next_month", "mean"),
        total_credit_limit=("limit_bal", "sum"),
        defaulter_limit_exposure=("defaulter_limit_exposure", "sum"),
        defaulter_bill_exposure=("defaulter_bill_exposure", "sum"),
        average_utilization=("utilization", "mean"),
    ).reset_index()
    result.insert(0, "segment_type", segment_name)
    result["share_of_total_limit_exposed_to_defaulters"] = result["defaulter_limit_exposure"] / working["limit_bal"].sum()
    return result


def save_chart(fig: plt.Figure, name: str) -> None:
    VISUALS_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(VISUALS_DIR / name, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


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
    dimensions = {
        "education": pd.read_csv(PROCESSED_DIR / "dim_education.csv").set_index("education_key")["education_label"].to_dict(),
        "marriage": pd.read_csv(PROCESSED_DIR / "dim_marriage.csv").set_index("marriage_key")["marriage_label"].to_dict(),
        "pay": pd.read_csv(PROCESSED_DIR / "dim_pay_status.csv").set_index("pay_code")["pay_status_label"].to_dict(),
    }
    frame["education_label"] = frame["education_key"].map(dimensions["education"])
    frame["marriage_label"] = frame["marriage_key"].map(dimensions["marriage"])
    frame["sex_label"] = frame["sex"].map({1: "Homme", 2: "Femme"}).fillna("Autre ou inconnu")
    frame["recent_delay_label"] = frame["risk_flag_recent_delay"].map({0: "Pas de retard récent", 1: "Retard récent"})

    total_clients = int(len(frame))
    total_limit = float(frame["limit_bal"].sum())
    defaulter_limit_exposure = float(frame.loc[frame["default_next_month"] == 1, "limit_bal"].sum())
    kpis = pd.DataFrame(
        [
            {
                "clients": total_clients,
                "defaulters": int(frame["default_next_month"].sum()),
                "default_rate": default_rate(frame["default_next_month"]),
                "total_credit_limit_ntd": total_limit,
                "average_credit_limit_ntd": float(frame["limit_bal"].mean()),
                "defaulter_credit_limit_exposure_ntd": defaulter_limit_exposure,
                "defaulter_share_of_total_limit": defaulter_limit_exposure / total_limit,
                "average_utilization": float(frame["utilization"].mean()),
                "average_bill_amt1_ntd": float(frame["bill_amt1"].mean()),
            }
        ]
    )
    write_csv(kpis, RESULTS_DIR / "portfolio_kpis.csv")

    segment_frames = [
        segment_statistics(frame, "age_band", "Âge"),
        segment_statistics(frame.assign(segment_education=frame["education_label"]), "segment_education", "Éducation"),
        segment_statistics(frame.assign(segment_marriage=frame["marriage_label"]), "segment_marriage", "État matrimonial"),
        segment_statistics(frame, "limit_band", "Limite de crédit"),
        segment_statistics(frame, "utilization_band", "Utilisation"),
        segment_statistics(frame.assign(segment_recent=frame["recent_delay_label"]), "segment_recent", "Retard récent"),
        segment_statistics(frame.assign(segment_sex=frame["sex_label"]), "segment_sex", "Sexe descriptif uniquement"),
    ]
    segments = pd.concat(segment_frames, ignore_index=True)
    write_csv(segments, RESULTS_DIR / "default_by_segment.csv")

    pay0 = segment_statistics(frame, "pay_0", "Statut pay_0")
    pay0["pay_code"] = pd.to_numeric(pay0["segment"], errors="coerce")
    pay0["pay_status_label"] = pay0["pay_code"].map(dimensions["pay"])
    write_csv(pay0.sort_values("pay_code"), RESULTS_DIR / "default_rate_by_pay0.csv")

    transition = frame.groupby(["pay_2", "pay_0"], observed=True).agg(
        customers=("client_id", "size"),
        default_count=("default_next_month", "sum"),
        default_rate=("default_next_month", "mean"),
    ).reset_index()
    transition["pay_2_total"] = transition.groupby("pay_2")["customers"].transform("sum")
    transition["row_share"] = transition["customers"] / transition["pay_2_total"]
    write_csv(transition.sort_values(["pay_2", "pay_0"]), RESULTS_DIR / "delinquency_transition.csv")

    utilization = segments.loc[segments["segment_type"] == "Utilisation"].copy()
    write_csv(utilization, RESULTS_DIR / "utilization_summary.csv")
    utilization_over1 = int((frame["utilization"] > 1).sum())
    write_csv(
        pd.DataFrame(
            [
                {"indicator": "Clients", "definition": "Nombre de clients distincts", "value": total_clients, "unit": "clients"},
                {"indicator": "Défauts le mois suivant", "definition": "Somme de default_next_month", "value": int(frame["default_next_month"].sum()), "unit": "clients"},
                {"indicator": "Taux de défaut", "definition": "Défauts / clients", "value": default_rate(frame["default_next_month"]), "unit": "proportion"},
                {"indicator": "Limite de crédit totale", "definition": "Somme de limit_bal", "value": total_limit, "unit": "NT$"},
                {"indicator": "Limite moyenne", "definition": "Moyenne de limit_bal", "value": float(frame["limit_bal"].mean()), "unit": "NT$"},
                {"indicator": "Exposition des défaillants", "definition": "Somme de limit_bal pour default_next_month = 1", "value": defaulter_limit_exposure, "unit": "NT$"},
                {"indicator": "Part de l’exposition des défaillants", "definition": "Exposition des défaillants / limite totale", "value": defaulter_limit_exposure / total_limit, "unit": "proportion"},
                {"indicator": "Utilisation moyenne", "definition": "Moyenne de bill_amt1 / limit_bal, bornée à 0–1,5", "value": float(frame["utilization"].mean()), "unit": "ratio"},
                {"indicator": "Clients avec utilisation supérieure à 100 %", "definition": "Nombre de clients avec utilization > 1", "value": utilization_over1, "unit": "clients"},
            ]
        ),
        RESULTS_DIR / "metrics_summary.csv",
    )

    set_plot_style()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    for axis, segment_type, title in zip(axes, ["Âge", "Éducation"], ["Par bande d’âge", "Par niveau d’éducation"]):
        data = segments.loc[segments["segment_type"] == segment_type]
        order = ["<25", "25-34", "35-44", "45-54", "55+"] if segment_type == "Âge" else ["Études supérieures", "Université", "Lycée", "Autre ou inconnu"]
        data = data.set_index("segment").reindex(order).dropna(subset=["default_rate"]).reset_index()
        axis.bar(data["segment"], data["default_rate"] * 100, color="#647D8E")
        axis.set_title(title)
        axis.set_ylabel("Défaut le mois suivant (%)")
        axis.tick_params(axis="x", rotation=20)
    fig.suptitle("Taux de défaut observé par segment")
    save_chart(fig, "default_rate_by_segment.png")

    fig, ax = plt.subplots(figsize=(10, 5.4))
    pay_plot = pay0.sort_values("pay_code")
    pay_labels = pay_plot["pay_status_label"].fillna(pay_plot["segment"])
    ax.barh(pay_labels, pay_plot["default_rate"] * 100, color="#718A9A")
    ax.invert_yaxis()
    ax.set_title("Le statut de remboursement récent est associé au défaut")
    ax.set_xlabel("Défaut le mois suivant (%)")
    ax.set_ylabel("Statut pay_0")
    save_chart(fig, "default_rate_by_pay0.png")

    matrix = transition.pivot(index="pay_2", columns="pay_0", values="row_share").fillna(0).sort_index().sort_index(axis=1)
    fig, ax = plt.subplots(figsize=(7.2, 6.0))
    image = ax.imshow(matrix.values, cmap="Greys", vmin=0, vmax=max(float(matrix.values.max()), 0.01), aspect="auto")
    ax.set_xticks(np.arange(len(matrix.columns)), [str(value) for value in matrix.columns])
    ax.set_yticks(np.arange(len(matrix.index)), [str(value) for value in matrix.index])
    ax.set_xlabel("Statut récent pay_0")
    ax.set_ylabel("Statut précédent pay_2")
    ax.set_title("Transition des statuts de paiement : part de la ligne")
    for row_index in range(matrix.shape[0]):
        for column_index in range(matrix.shape[1]):
            value = matrix.iloc[row_index, column_index]
            if value > 0:
                ax.text(column_index, row_index, f"{value:.0%}", ha="center", va="center", color="white" if value >= 0.50 else "black", fontsize=7)
    fig.colorbar(image, ax=ax, label="Part des clients")
    save_chart(fig, "delinquency_transition_heatmap.png")

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    util_plot = utilization.set_index("segment").reindex(["<30 %", "30-<60 %", "60-100 %", ">100 %"]).dropna(subset=["default_rate"])
    ax.bar(util_plot.index, util_plot["default_rate"] * 100, color="#7C8F9A")
    ax.set_title("Défaut observé selon la bande d’utilisation")
    ax.set_ylabel("Défaut le mois suivant (%)")
    ax.set_xlabel("Utilisation plafonnée")
    save_chart(fig, "utilization_vs_default.png")

    print(f"Analyse descriptive terminée : taux de défaut {default_rate(frame['default_next_month']):.4%}; {len(segments)} lignes de segments.")


if __name__ == "__main__":
    main()
