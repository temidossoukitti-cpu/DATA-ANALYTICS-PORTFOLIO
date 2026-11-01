"""Analyse descriptive pondérée de la conversion campagne et graphiques."""
from __future__ import annotations

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pipeline_utils import (
    AGE_BANDS, CAMPAIGN_BANDS, ROOT, MONTH_LABELS,
    JOB_LABELS, EDUCATION_LABELS, MARITAL_LABELS,
    CONTACT_LABELS, POUTCOME_LABELS, fr_num, fr_pct,
)


def main() -> None:
    fact = pd.read_csv(ROOT / "data/processed/fact_campaign.csv")
    dim_outcome = pd.read_csv(ROOT / "data/processed/dim_outcome.csv")
    dim_job = pd.read_csv(ROOT / "data/processed/dim_job.csv")
    dim_education = pd.read_csv(ROOT / "data/processed/dim_education.csv")
    dim_month = pd.read_csv(ROOT / "data/processed/dim_month.csv")
    dim_contact = pd.read_csv(ROOT / "data/processed/dim_contact.csv")
    dim_poutcome = pd.read_csv(ROOT / "data/processed/dim_poutcome.csv")
    dim_age_band = pd.read_csv(ROOT / "data/processed/dim_age_band.csv")
    dim_campaign_band = pd.read_csv(ROOT / "data/processed/dim_campaign_band.csv")
    dim_marital = pd.read_csv(ROOT / "data/processed/dim_marital.csv")

    pop = int(fact["outcome_key"].sum())
    total = len(fact)
    conv_rate = fr_pct(pop / total)

    overall = pd.DataFrame([
        {"metric": "campaign_rows", "value": total, "unit": "campaigns", "source": "results/overall_kpis.csv"},
        {"metric": "subscriptions", "value": pop, "unit": "subscriptions", "source": "results/overall_kpis.csv"},
        {"metric": "conversion_rate", "value": pop / total, "unit": "proportion", "source": "results/overall_kpis.csv"},
    ])
    (ROOT / "results").mkdir(exist_ok=True)
    overall.to_csv(ROOT / "results/overall_kpis.csv", index=False, encoding="utf-8")

    # Conversion by month
    month_conv = (
        fact.groupby("month_key")
        .agg(rows=("campaign_id", "count"), subscriptions=("outcome_key", "sum"))
        .reset_index()
    )
    month_conv["conversion_rate"] = month_conv["subscriptions"] / month_conv["rows"]
    month_labels = dim_month.set_index("month_key")["label_fr"]
    month_conv["label_fr"] = month_conv["month_key"].map(month_labels)
    month_conv = month_conv.sort_values("month_key")
    month_conv.to_csv(ROOT / "results/conversion_by_month.csv", index=False, encoding="utf-8")

    # Conversion by job
    job_conv = (
        fact.groupby("job_key")
        .agg(rows=("campaign_id", "count"), subscriptions=("outcome_key", "sum"))
        .reset_index()
    )
    job_conv["conversion_rate"] = job_conv["subscriptions"] / job_conv["rows"]
    job_conv = job_conv.merge(dim_job[["job_key", "label_fr", "sort_order"]], on="job_key")
    job_conv = job_conv.sort_values("sort_order")
    job_conv.to_csv(ROOT / "results/conversion_by_job.csv", index=False, encoding="utf-8")

    # Conversion by poutcome
    poutcome_conv = (
        fact.groupby("poutcome_key")
        .agg(rows=("campaign_id", "count"), subscriptions=("outcome_key", "sum"))
        .reset_index()
    )
    poutcome_conv["conversion_rate"] = poutcome_conv["subscriptions"] / poutcome_conv["rows"]
    poutcome_conv = poutcome_conv.merge(dim_poutcome[["poutcome_key", "label_fr", "sort_order"]], on="poutcome_key")
    poutcome_conv = poutcome_conv.sort_values("sort_order")
    poutcome_conv.to_csv(ROOT / "results/conversion_by_poutcome.csv", index=False, encoding="utf-8")

    # Conversion by age band
    age_conv = (
        fact.groupby("age_band_key")
        .agg(rows=("campaign_id", "count"), subscriptions=("outcome_key", "sum"))
        .reset_index()
    )
    age_conv["conversion_rate"] = age_conv["subscriptions"] / age_conv["rows"]
    age_conv = age_conv.merge(dim_age_band[["age_band_key", "label_fr", "sort_order"]], on="age_band_key")
    age_conv = age_conv.sort_values("sort_order")
    age_conv.to_csv(ROOT / "results/conversion_by_age_band.csv", index=False, encoding="utf-8")

    # Conversion by campaign band
    camp_conv = (
        fact.groupby("campaign_band_key")
        .agg(rows=("campaign_id", "count"), subscriptions=("outcome_key", "sum"))
        .reset_index()
    )
    camp_conv["conversion_rate"] = camp_conv["subscriptions"] / camp_conv["rows"]
    camp_conv = camp_conv.merge(dim_campaign_band[["campaign_band_key", "label_fr", "sort_order"]], on="campaign_band_key")
    camp_conv = camp_conv.sort_values("sort_order")
    camp_conv.to_csv(ROOT / "results/conversion_by_campaign_band.csv", index=False, encoding="utf-8")

    # Conversion by marital
    marital_conv = (
        fact.groupby("marital_key")
        .agg(rows=("campaign_id", "count"), subscriptions=("outcome_key", "sum"))
        .reset_index()
    )
    marital_conv["conversion_rate"] = marital_conv["subscriptions"] / marital_conv["rows"]
    marital_conv = marital_conv.merge(dim_marital[["marital_key", "label_fr", "sort_order"]], on="marital_key")
    marital_conv = marital_conv.sort_values("sort_order")
    marital_conv.to_csv(ROOT / "results/conversion_by_marital.csv", index=False, encoding="utf-8")

    # Conversion by education
    edu_conv = (
        fact.groupby("education_key")
        .agg(rows=("campaign_id", "count"), subscriptions=("outcome_key", "sum"))
        .reset_index()
    )
    edu_conv["conversion_rate"] = edu_conv["subscriptions"] / edu_conv["rows"]
    edu_conv = edu_conv.merge(dim_education[["education_key", "label_fr", "sort_order"]], on="education_key")
    edu_conv = edu_conv.sort_values("sort_order")
    edu_conv.to_csv(ROOT / "results/conversion_by_education.csv", index=False, encoding="utf-8")

    # Conversion by contact
    contact_conv = (
        fact.groupby("contact_key")
        .agg(rows=("campaign_id", "count"), subscriptions=("outcome_key", "sum"))
        .reset_index()
    )
    contact_conv["conversion_rate"] = contact_conv["subscriptions"] / contact_conv["rows"]
    contact_conv = contact_conv.merge(dim_contact[["contact_key", "label_fr", "sort_order"]], on="contact_key")
    contact_conv = contact_conv.sort_values("sort_order")
    contact_conv.to_csv(ROOT / "results/conversion_by_contact.csv", index=False, encoding="utf-8")

    # Overall segment table summarizing lift for recommendations
    segment_rows = [
        ("mois", month_conv["label_fr"].tolist(), month_conv["conversion_rate"].tolist()),
        ("emploi", job_conv["label_fr"].tolist(), job_conv["conversion_rate"].tolist()),
        ("poutcome", poutcome_conv["label_fr"].tolist(), poutcome_conv["conversion_rate"].tolist()),
        ("groupe_age", age_conv["label_fr"].tolist(), age_conv["conversion_rate"].tolist()),
        ("campagnes", camp_conv["label_fr"].tolist(), camp_conv["conversion_rate"].tolist()),
        ("état_civil", marital_conv["label_fr"].tolist(), marital_conv["conversion_rate"].tolist()),
        ("niveau_etude", edu_conv["label_fr"].tolist(), edu_conv["conversion_rate"].tolist()),
        ("canal_contact", contact_conv["label_fr"].tolist(), contact_conv["conversion_rate"].tolist()),
    ]
    seg_df = pd.DataFrame({
        "dimension": [s[0] for s in segment_rows],
        "labels": [s[1] for s in segment_rows],
        "rates": [s[2] for s in segment_rows],
    })
    seg_df.to_csv(ROOT / "results/conversion_by_segment.csv", index=False, encoding="utf-8")

    # Visuals
    fig, ax = plt.subplots(figsize=(9.2, 5.1))
    bars = ax.bar(month_conv["label_fr"], month_conv["conversion_rate"] * 100, color="#315a7d", width=0.6)
    ax.set_title("Taux de conversion par mois")
    ax.set_ylabel("Conversions pondérées / campagnes (%)")
    ax.set_xlabel("Mois")
    for bar, value in zip(bars, month_conv["conversion_rate"] * 100):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.2f}%", ha="center", va="bottom", fontsize=9)
    style_axis(ax); fig.tight_layout(); fig.savefig(ROOT / "visuals/conversion_by_month.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10.4, 5.2))
    bars = ax.bar(job_conv["label_fr"], job_conv["conversion_rate"] * 100, color="#315a7d", width=0.6)
    ax.set_title("Taux de conversion par métier")
    ax.set_ylabel("Conversions pondérées / campagnes (%)")
    ax.set_xlabel("Métier")
    for bar, value in zip(bars, job_conv["conversion_rate"] * 100):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.2f}%", ha="center", va="bottom", fontsize=9)
    ax.tick_params(axis="x", rotation=28)
    style_axis(ax); fig.tight_layout(); fig.savefig(ROOT / "visuals/conversion_by_job.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.2, 5.1))
    bars = ax.bar(poutcome_conv["label_fr"], poutcome_conv["conversion_rate"] * 100, color="#315a7d", width=0.6)
    ax.set_title("Taux de conversion par issue de campagne précédente")
    ax.set_ylabel("Conversions pondérées / campagnes (%)")
    ax.set_xlabel("Issue précédente")
    for bar, value in zip(bars, poutcome_conv["conversion_rate"] * 100):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.2f}%", ha="center", va="bottom", fontsize=9)
    style_axis(ax); fig.tight_layout(); fig.savefig(ROOT / "visuals/conversion_by_poutcome.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.2, 5.1))
    bars = ax.bar(age_conv["label_fr"], age_conv["conversion_rate"] * 100, color="#315a7d", width=0.6)
    ax.set_title("Taux de conversion par groupe d'âge")
    ax.set_ylabel("Conversions pondérées / campagnes (%)")
    ax.set_xlabel("Groupe d'âge")
    for bar, value in zip(bars, age_conv["conversion_rate"] * 100):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.2f}%", ha="center", va="bottom", fontsize=9)
    style_axis(ax); fig.tight_layout(); fig.savefig(ROOT / "visuals/conversion_by_age_band.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.2, 5.1))
    bars = ax.bar(camp_conv["label_fr"], camp_conv["conversion_rate"] * 100, color="#315a7d", width=0.6)
    ax.set_title("Taux de conversion par nombre de contacts campagne")
    ax.set_ylabel("Conversions pondérées / campagnes (%)")
    ax.set_xlabel("Nombre de contacts")
    for bar, value in zip(bars, camp_conv["conversion_rate"] * 100):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.2f}%", ha="center", va="bottom", fontsize=9)
    style_axis(ax); fig.tight_layout(); fig.savefig(ROOT / "visuals/conversion_by_campaign_band.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.2, 5.1))
    bars = ax.bar(marital_conv["label_fr"], marital_conv["conversion_rate"] * 100, color="#315a7d", width=0.6)
    ax.set_title("Taux de conversion par état civil")
    ax.set_ylabel("Conversions pondérées / campagnes (%)")
    ax.set_xlabel("État civil")
    for bar, value in zip(bars, marital_conv["conversion_rate"] * 100):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.2f}%", ha="center", va="bottom", fontsize=9)
    style_axis(ax); fig.tight_layout(); fig.savefig(ROOT / "visuals/conversion_by_marital.png", dpi=160); plt.close(fig)

    # Coverage gaps CSV
    gaps = pd.DataFrame([
        {"dimension": "identifiant client", "available": False, "handling": "Aucun identifiant unique; les doublons sont conservés au niveau ligne."},
        {"dimension": "revenu client", "available": False, "handling": "Non fourni par la source."},
        {"dimension": "date civile", "available": False, "handling": "Aucune date civile; seule une fenêtre relative (6 h) existe."},
        {"dimension": "durée utilisable pour modélisation", "available": False, "handling": "Exclue du modèle (fuite d'information)."},
    ])
    gaps.to_csv(ROOT / "results/coverage_gaps.csv", index=False, encoding="utf-8")

    n_visuals = len([f for f in os.listdir(ROOT / "visuals") if f.endswith(".png")])
    print(f"Analyse descriptive terminée. Taux source : {conv_rate}.")
    print(f"Segments générés : {len(seg_df)}; visuals écrits : {n_visuals}.")


def style_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.2, linewidth=0.7)
    ax.set_axisbelow(True)


if __name__ == "__main__":
    main()
