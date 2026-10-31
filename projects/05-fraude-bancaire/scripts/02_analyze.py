"""Analyse descriptive pondérée de la fraude et graphiques sans sémantique inventée."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pipeline_utils import AMOUNT_BANDS, ROOT, TIME_WINDOWS, add_bands, load_sample, population_values


BLUE = "#315a7d"
GOLD = "#c69214"
GRAY = "#7b8794"


def write_group_metrics(frame: pd.DataFrame, key: str, label_map: dict[int, str]) -> pd.DataFrame:
    rows = []
    for value in sorted(frame[key].dropna().unique()):
        part = frame.loc[frame[key].eq(value)]
        weights = part["sampling_weight"].to_numpy(dtype=float)
        y = part["Class"].to_numpy(dtype=int)
        amount = part["Amount"].to_numpy(dtype=float)
        total = float(weights.sum())
        fraud = float(np.sum(weights * y))
        total_amount = float(np.sum(weights * amount))
        fraud_amount = float(np.sum(weights * amount * y))
        rows.append({
            "group_key": int(value), "label_fr": label_map[int(value)],
            "sample_rows": int(len(part)), "transactions_estimate": total,
            "fraud_transactions_estimate": fraud,
            "fraud_rate": fraud / total if total else np.nan,
            "amount_estimate": total_amount,
            "fraud_amount_estimate": fraud_amount,
            "fraud_amount_share": fraud_amount / total_amount if total_amount else np.nan,
        })
    return pd.DataFrame(rows)


def style_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.2, linewidth=0.7)
    ax.set_axisbelow(True)


def main() -> None:
    raw = load_sample()
    frame = add_bands(raw)
    pop = population_values()
    pop_total = float(pop["transactions_total"])
    pop_fraud = float(pop["transactions_fraud"])
    pop_rate = float(pop["fraud_rate"])
    design_weight = frame["sampling_weight"].to_numpy(dtype=float)
    y = frame["Class"].to_numpy(dtype=int)
    amount = frame["Amount"].to_numpy(dtype=float)
    weighted_total = float(design_weight.sum())
    weighted_fraud = float(np.sum(design_weight * y))
    weighted_amount = float(np.sum(design_weight * amount))
    weighted_fraud_amount = float(np.sum(design_weight * amount * y))

    overall = pd.DataFrame([
        {"metric": "transactions_population_exact", "value": pop_total, "unit": "transactions", "source": "results/population_kpis.csv"},
        {"metric": "fraud_transactions_population_exact", "value": pop_fraud, "unit": "transactions", "source": "results/population_kpis.csv"},
        {"metric": "fraud_rate_population_exact", "value": pop_rate, "unit": "proportion", "source": "results/population_kpis.csv"},
        {"metric": "fraud_rate_weighted_sample", "value": weighted_fraud / weighted_total, "unit": "proportion", "source": "committed sample and sampling_weight"},
        {"metric": "amount_total_population_exact", "value": float(pop["amount_total"]), "unit": "dataset amount units", "source": "results/population_kpis.csv"},
        {"metric": "fraud_amount_population_exact", "value": float(pop["amount_fraud"]), "unit": "dataset amount units", "source": "results/population_kpis.csv"},
        {"metric": "amount_total_weighted_sample", "value": weighted_amount, "unit": "dataset amount units", "source": "committed sample and sampling_weight"},
        {"metric": "fraud_amount_weighted_sample", "value": weighted_fraud_amount, "unit": "dataset amount units", "source": "committed sample and sampling_weight"},
        {"metric": "unweighted_sample_fraud_rate", "value": float(y.mean()), "unit": "proportion", "source": "descriptive only; oversampled fraud class"},
    ])
    (ROOT / "results").mkdir(exist_ok=True)
    overall.to_csv(ROOT / "results/overall_kpis.csv", index=False, encoding="utf-8")

    amount_labels = {row["amount_band_key"]: row["label_fr"] for row in AMOUNT_BANDS}
    time_labels = {row["time_window_key"]: row["label_fr"] for row in TIME_WINDOWS}
    by_amount = write_group_metrics(frame, "amount_band_key", amount_labels)
    by_time = write_group_metrics(frame, "time_window_key", time_labels)
    by_amount.to_csv(ROOT / "results/fraud_by_amount_band.csv", index=False, encoding="utf-8")
    by_time.to_csv(ROOT / "results/fraud_by_time_window.csv", index=False, encoding="utf-8")

    unavailable = pd.DataFrame([{
        "dimension": "type de transaction", "availability": "NON DISPONIBLE",
        "fraud_rate": np.nan,
        "reason": "La source OpenML ne contient pas de colonne type/canal; V1–V28 sont anonymisées par PCA. Aucun type métier n'est inféré.",
    }])
    unavailable.to_csv(ROOT / "results/fraud_by_transaction_type.csv", index=False, encoding="utf-8")
    pd.DataFrame([
        {"field": "type/canal de transaction", "available": False, "handling": "Taux non calculable; conserver cette lacune dans les recommandations."},
        {"field": "devise", "available": False, "handling": "Montants rapportés en unités du dataset, sans symbole monétaire."},
        {"field": "date civile", "available": False, "handling": "Time est relatif au premier enregistrement; fenêtres de six heures relatives."},
        {"field": "identifiant client", "available": False, "handling": "Aucune déduplication au niveau client ou compte possible."},
    ]).to_csv(ROOT / "results/coverage_gaps.csv", index=False, encoding="utf-8")

    visuals = ROOT / "visuals"
    visuals.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(9.2, 5.1))
    bars = ax.bar(by_amount["label_fr"], by_amount["fraud_rate"] * 100, color=BLUE, width=0.64)
    ax.set_title("Fraude observée par bande de montant")
    ax.set_ylabel("Fraudes pondérées / transactions pondérées (%)")
    ax.set_xlabel("Unités de montant du dataset; seuils descriptifs")
    for bar, value in zip(bars, by_amount["fraud_rate"] * 100):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.3f}%", ha="center", va="bottom", fontsize=9)
    style_axis(ax); fig.tight_layout(); fig.savefig(visuals / "fraud_rate_by_amount_band.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10.4, 5.2))
    bars = ax.bar(by_time["label_fr"], by_time["fraud_rate"] * 100, color=GOLD, width=0.68)
    ax.set_title("Fraude observée par fenêtre relative de six heures")
    ax.set_ylabel("Fraudes pondérées / transactions pondérées (%)")
    ax.set_xlabel("Fenêtre depuis la première transaction; pas une heure civile")
    ax.tick_params(axis="x", rotation=28)
    for bar, value in zip(bars, by_time["fraud_rate"] * 100):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.3f}%", ha="center", va="bottom", fontsize=8)
    style_axis(ax); fig.tight_layout(); fig.savefig(visuals / "fraud_rate_by_time_window.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    bins = np.linspace(0, np.log10(max(float(frame["Amount"].max()), 1) + 1), 45)
    for label, class_value, color in [("Légitime", 0, GRAY), ("Fraude", 1, GOLD)]:
        part = frame.loc[frame["Class"].eq(class_value)]
        ax.hist(np.log10(part["Amount"].to_numpy(dtype=float) + 1), bins=bins,
                weights=part["sampling_weight"].to_numpy(dtype=float), density=True,
                histtype="step", linewidth=1.8, label=label, color=color)
    ax.set_title("Distribution pondérée des montants")
    ax.set_xlabel("log10(Amount + 1); unité monétaire non précisée")
    ax.set_ylabel("Densité pondérée")
    ax.legend(frameon=False)
    style_axis(ax); fig.tight_layout(); fig.savefig(visuals / "amount_distribution_by_class.png", dpi=160); plt.close(fig)

    print(f"Analyse descriptive terminée : taux exact={pop_rate:.6%}; taux pondéré échantillon={weighted_fraud/weighted_total:.6%}.")
    print(f"Segments : {len(by_amount)} bandes de montant, {len(by_time)} fenêtres; type de transaction absent et explicitement signalé.")


if __name__ == "__main__":
    main()
