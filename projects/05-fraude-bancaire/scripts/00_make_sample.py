"""Crée l'échantillon pondéré depuis le Parquet officiel complet.

Le fichier source (>50 Mo) n'est jamais versionné. Cette étape de préparation
s'exécute une fois; le pipeline run_all.py utilise ensuite l'échantillon livré.
Usage depuis la racine du projet:
  python scripts/00_make_sample.py --input data/raw/openml_43627_full.parquet
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent
EXPECTED_COLUMNS = ["Time", *[f"V{i}" for i in range(1, 29)], "Amount", "Class"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def add_metric(rows: list[dict], metric: str, value, unit: str, scope: str, definition: str) -> None:
    rows.append({"metric": metric, "value": value, "unit": unit, "scope": scope, "definition": definition})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/raw/openml_43627_full.parquet")
    parser.add_argument("--sample-output", type=Path, default=ROOT / "data/processed/transactions_sample.parquet")
    parser.add_argument("--population-output", type=Path, default=ROOT / "results/population_kpis.csv")
    parser.add_argument("--legitimate-sample-size", type=int, default=25_000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    source = args.input
    if not source.is_file():
        raise SystemExit(f"Fichier source absent: {source}. Télécharger l'URL officielle décrite dans data/raw/SOURCE.md.")
    full = pd.read_parquet(source)
    if list(full.columns) != EXPECTED_COLUMNS:
        raise SystemExit(f"Schéma inattendu. Colonnes reçues: {list(full.columns)}")
    if full["Class"].isna().any() or not set(full["Class"].unique()).issubset({0, 1}):
        raise SystemExit("La cible Class doit être complète et binaire {0, 1}.")
    if full.select_dtypes(include=[np.number]).isna().any().any():
        raise SystemExit("La source contient des valeurs manquantes; examiner avant échantillonnage.")
    if not np.isfinite(full.select_dtypes(include=[np.number]).to_numpy()).all():
        raise SystemExit("La source contient des valeurs numériques non finies.")

    fraud = full.loc[full["Class"].eq(1)].copy()
    legitimate = full.loc[full["Class"].eq(0)].copy()
    if args.legitimate_sample_size <= 0 or args.legitimate_sample_size > len(legitimate):
        raise SystemExit("La taille de l'échantillon légitime doit être entre 1 et l'effectif légitime disponible.")

    full = full.copy()
    full.insert(0, "transaction_id", np.arange(len(full), dtype=np.int64))
    fraud = full.loc[full["Class"].eq(1)].copy()
    legitimate = full.loc[full["Class"].eq(0)].copy()
    sampled_legitimate = legitimate.sample(n=args.legitimate_sample_size, random_state=args.seed).copy()
    fraud["sampling_weight"] = 1.0
    sampled_legitimate["sampling_weight"] = len(legitimate) / len(sampled_legitimate)
    sample = pd.concat([sampled_legitimate, fraud], ignore_index=True).sort_values("transaction_id", kind="stable")
    sample = sample.reset_index(drop=True)

    features = [column for column in EXPECTED_COLUMNS if column != "Class"]
    conflict_count = int(full.groupby(features, dropna=False)["Class"].nunique().gt(1).sum())
    duplicate_rows = int(full.duplicated(subset=EXPECTED_COLUMNS).sum())
    duplicate_fraud = int(full.loc[full["Class"].eq(1)].duplicated(subset=EXPECTED_COLUMNS).sum())
    duplicate_legitimate = int(full.loc[full["Class"].eq(0)].duplicated(subset=EXPECTED_COLUMNS).sum())
    source_hash = sha256(source)

    metrics: list[dict] = []
    n_total = len(full)
    n_fraud = int(full["Class"].eq(1).sum())
    n_legitimate = int(full["Class"].eq(0).sum())
    total_amount = float(full["Amount"].sum())
    fraud_amount = float(full.loc[full["Class"].eq(1), "Amount"].sum())
    add_metric(metrics, "transactions_total", n_total, "transactions", "full_source", "Toutes les lignes du Parquet officiel, sans déduplication.")
    add_metric(metrics, "transactions_fraud", n_fraud, "transactions", "full_source", "Nombre de lignes Class=1 dans le Parquet officiel.")
    add_metric(metrics, "transactions_legitimes", n_legitimate, "transactions", "full_source", "Nombre de lignes Class=0 dans le Parquet officiel.")
    add_metric(metrics, "fraud_rate", n_fraud / n_total, "proportion", "full_source", "transactions_fraud / transactions_total; estimation exacte du fichier source.")
    add_metric(metrics, "amount_total", total_amount, "unités de montant du dataset", "full_source", "Somme de Amount; la source ne précise aucune devise.")
    add_metric(metrics, "amount_fraud", fraud_amount, "unités de montant du dataset", "full_source", "Somme de Amount pour Class=1; exposition labellisée fraude, pas une perte recouvrée observée.")
    add_metric(metrics, "amount_legitime", total_amount - fraud_amount, "unités de montant du dataset", "full_source", "Somme de Amount pour Class=0.")
    add_metric(metrics, "fraud_amount_share", fraud_amount / total_amount if total_amount else 0.0, "proportion", "full_source", "amount_fraud / amount_total.")
    add_metric(metrics, "amount_mean", float(full["Amount"].mean()), "unités de montant du dataset", "full_source", "Moyenne de Amount sur toutes les transactions.")
    add_metric(metrics, "amount_median", float(full["Amount"].median()), "unités de montant du dataset", "full_source", "Médiane de Amount sur toutes les transactions.")
    add_metric(metrics, "amount_max", float(full["Amount"].max()), "unités de montant du dataset", "full_source", "Maximum de Amount.")
    add_metric(metrics, "exact_duplicate_rows", duplicate_rows, "lignes au-delà de la première occurrence", "full_source", "Doublons exacts sur Time, V1–V28, Amount et Class; conservés et regroupés au split.")
    add_metric(metrics, "exact_duplicate_fraud_rows", duplicate_fraud, "lignes au-delà de la première occurrence", "full_source", "Doublons exacts de classe fraude; conservés, aucun fraud row source n'est supprimé.")
    add_metric(metrics, "exact_duplicate_legitimate_rows", duplicate_legitimate, "lignes au-delà de la première occurrence", "full_source", "Doublons exacts de classe légitime; conservés dans la population source.")
    add_metric(metrics, "feature_groups_with_label_conflict", conflict_count, "groupes", "full_source", "Groupes d'attributs hors cible portant des classes différentes; attendu 0.")
    add_metric(metrics, "missing_cells", int(full[EXPECTED_COLUMNS].isna().sum().sum()), "cellules", "full_source", "Cellules manquantes dans les colonnes source.")
    add_metric(metrics, "negative_amount_rows", int(full["Amount"].lt(0).sum()), "lignes", "full_source", "Amount négatif; règle de contrôle, attendu 0.")
    add_metric(metrics, "negative_time_rows", int(full["Time"].lt(0).sum()), "lignes", "full_source", "Time négatif; règle de contrôle, attendu 0.")
    add_metric(metrics, "time_max_seconds", float(full["Time"].max()), "secondes depuis la première transaction", "full_source", "Maximum Time déclaré dans le descriptif OpenML.")
    add_metric(metrics, "source_size_bytes", source.stat().st_size, "octets", "full_source", "Taille exacte du Parquet téléchargé depuis OpenML.")
    add_metric(metrics, "source_sha256", source_hash, "SHA-256", "full_source", "Empreinte du fichier Parquet complet; le fichier complet n'est pas redistribué par le dépôt.")
    add_metric(metrics, "sample_rows", len(sample), "transactions", "committed_sample", "Toutes les fraudes et l'échantillon aléatoire des transactions légitimes.")
    add_metric(metrics, "sample_fraud_rows", int(sample["Class"].eq(1).sum()), "transactions", "committed_sample", "Toutes les lignes Class=1 du fichier source.")
    add_metric(metrics, "sample_legitimate_rows", int(sample["Class"].eq(0).sum()), "transactions", "committed_sample", "Lignes Class=0 tirées sans remise avec random_state indiqué.")
    add_metric(metrics, "sample_legitimate_weight", len(legitimate) / len(sampled_legitimate), "poids par ligne", "committed_sample", "N légitimes source / N légitimes échantillonnées.")
    add_metric(metrics, "sample_fraud_weight", 1.0, "poids par ligne", "committed_sample", "Toutes les lignes fraude sont conservées; poids de recensement égal à 1.")
    add_metric(metrics, "sample_seed", args.seed, "graine aléatoire", "committed_sample", "Graine de l'échantillonnage reproductible.")

    args.sample_output.parent.mkdir(parents=True, exist_ok=True)
    args.population_output.parent.mkdir(parents=True, exist_ok=True)
    sample.to_parquet(args.sample_output, index=False)
    pd.DataFrame(metrics).to_csv(args.population_output, index=False, encoding="utf-8")
    print(f"Source: {n_total:,} lignes, {n_fraud:,} fraudes; doublons exacts conservés: {duplicate_rows:,}.")
    print(f"Échantillon: {len(sample):,} lignes ({len(fraud):,} fraudes + {len(sampled_legitimate):,} légitimes), poids légitime={len(legitimate)/len(sampled_legitimate):.6f}.")
    print(f"Parquet complet: {source.stat().st_size:,} octets; SHA-256={source_hash}.")


if __name__ == "__main__":
    main()
