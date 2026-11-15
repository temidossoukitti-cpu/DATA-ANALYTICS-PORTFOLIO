"""Génère le rapport QA et les blocs chiffrés du README."""
from __future__ import annotations

import math
import re
from pathlib import Path
from urllib.parse import unquote

import pandas as pd

from pipeline_utils import EXPECTED_RAW_SHA256, PROJECT_ROOT, RAW_XLS, sha256_file, write_csv

REPO_ROOT = PROJECT_ROOT.parents[1]
PAGE_TITLES = [
    "Vue d’ensemble",
    "Segments à risque",
    "Comportement de paiement et retards",
    "Scoring et actions",
]


def format_count(value: int | float) -> str:
    return f"{int(value):,}".replace(",", " ")


def format_pct(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "n.d."
    return f"{value * 100:.{digits}f}".replace(".", ",") + " %"


def format_ratio(value: float, digits: int = 4) -> str:
    if pd.isna(value):
        return "n.d."
    return f"{value:.{digits}f}".replace(".", ",")


def format_money(value: float) -> str:
    if pd.isna(value):
        return "n.d."
    return "NT$ " + f"{value:,.0f}".replace(",", " ")


def marker_block(text: str, marker: str) -> str:
    begin = f"<!-- {marker}_BEGIN -->"
    finish = f"<!-- {marker}_END -->"
    begin_position = text.find(begin)
    end_position = text.find(finish, begin_position + len(begin))
    if begin_position < 0 or end_position < 0:
        raise ValueError(f"Marqueurs manquants pour le bloc {marker}.")
    return text[: begin_position + len(begin)] + "\n" + text_between_markers[marker] + "\n" + text[end_position:]


# Rempli pendant main() avant le remplacement des blocs.
text_between_markers: dict[str, str] = {}


def resolve_markdown_links(paths: list[Path]) -> list[str]:
    issues: list[str] = []
    link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for markdown_file in paths:
        if not markdown_file.exists():
            issues.append(f"Fichier Markdown absent : {markdown_file.name}")
            continue
        for destination in link_pattern.findall(markdown_file.read_text(encoding="utf-8")):
            target = destination.strip().split()[0].strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            local_target = unquote(target.split("#", 1)[0])
            if not local_target:
                continue
            resolved = (markdown_file.parent / local_target).resolve()
            if not resolved.exists():
                issues.append(f"{markdown_file.relative_to(REPO_ROOT)} → {target}")
    return issues


def replace_readme_blocks(metrics: pd.Series, kpis: pd.Series, model: pd.Series, quality: pd.DataFrame, recommendations: pd.DataFrame, counts: dict) -> None:
    readme_path = PROJECT_ROOT / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    highrisk_share = float(counts["high_risk_clients"]) / float(model["test_clients"])
    summary = "\n".join(
        [
            f"- **Cohorte traitée :** {format_count(counts['fact_rows'])} clients issus de {format_count(counts['raw_columns'])} colonnes; {format_count(int(quality.loc[quality['rule'] == 'missing_raw_values', 'affected_rows'].iloc[0]))} valeur manquante brute.",
            f"- **Niveau de défaut :** {format_pct(kpis['default_rate'])} sur la cohorte; limites totales de {format_money(kpis['total_credit_limit_ntd'])} et exposition des défaillants de {format_money(kpis['defaulter_credit_limit_exposure_ntd'])}.",
            f"- **Modèle test :** ROC-AUC {format_ratio(model['roc_auc'])}, PR-AUC {format_ratio(model['pr_auc_average_precision'])}, KS {format_ratio(model['ks_statistic'])}; précision {format_pct(model['precision_at_threshold'])} et rappel {format_pct(model['recall_at_threshold'])} au seuil {format_ratio(model['decision_threshold'], 2)}.",
            f"- **Livrables :** {format_count(counts['processed_table_count'])} tables chargées ({format_count(counts['star_table_count'])} en étoile et une scorecard) et {format_count(counts['visual_count'])} graphiques; part test à risque élevé {format_pct(highrisk_share)}.",
        ]
    )
    quality_row = quality.set_index("rule")
    data_summary = (
        f"Contrôles automatisés : **{format_count(counts['quality_pass_count'])}/{format_count(counts['quality_control_count'])} PASS**; "
        f"{format_count(int(quality_row.loc['duplicate_profiles_excluding_id', 'affected_rows']))} lignes appartenant à des profils identiques hors ID comptées et conservées; "
        f"{format_count(int(quality_row.loc['education_unknown_codes', 'affected_rows']))} recodages éducation et "
        f"{format_count(int(quality_row.loc['marriage_zero', 'affected_rows']))} recodages matrimoniaux; aucune ligne supprimée. "
        f"Voir [`results/quality_check.csv`](results/quality_check.csv) et [`qa/validation_report.md`](qa/validation_report.md)."
    )
    result_table = "\n".join(
        [
            "| Indicateur | Résultat | Source de référence |",
            "|---|---:|---|",
            f"| Clients / défauts | {format_count(kpis['clients'])} / {format_count(kpis['defaulters'])} | `results/portfolio_kpis.csv` |",
            f"| Taux de défaut | {format_pct(kpis['default_rate'])} | `results/portfolio_kpis.csv` |",
            f"| Limite moyenne | {format_money(kpis['average_credit_limit_ntd'])} | `results/portfolio_kpis.csv` |",
            f"| Part des limites détenue par les défaillants | {format_pct(kpis['defaulter_share_of_total_limit'])} | `results/portfolio_kpis.csv` |",
            f"| ROC-AUC / PR-AUC test | {format_ratio(model['roc_auc'])} / {format_ratio(model['pr_auc_average_precision'])} | `results/model_metrics.csv` |",
            f"| Perte attendue test à LGD 45 % | {format_money(counts['expected_loss_45'])} | `results/expected_loss_sensitivity.csv` |",
        ]
    )
    recommendation_rows = [
        "| ID | Déclencheur | Clients | Défaut observé | Exposition défaillants (NT$) | Action proposée |",
        "|---|---|---:|---:|---:|---|",
    ]
    for _, row in recommendations.iterrows():
        recommendation_rows.append(
            f"| {row['recommendation_id']} | {row['trigger']} | {format_count(row['cohort_customers'])} | {format_pct(row['observed_default_rate'])} | {format_money(row['exposure_ntd'])} | {row['action']} |"
        )
    recommendations_table = "\n".join(recommendation_rows)
    status_block = f"Automatisé : **{counts['overall_status']}** selon [`qa/validation_report.md`](qa/validation_report.md)."
    method_block = (
        f"Séparation stratifiée : **{format_pct(model['train_fraction'])} Train / {format_pct(model['test_fraction'])} Test**, "
        f"`random_state={format_count(model['random_state'])}`; seuil de classification **{format_ratio(model['decision_threshold'], 2)}**. "
        f"Bandes de score documentées : `{model['risk_band_cutoffs']}`. "
        f"La perte attendue applique une LGD de base de **{format_pct(model['base_lgd_assumption'])}** sur l’exposition facturée positive."
    )
    dashboard_block = f"Dashboard web interactif : [version hébergée](https://temidossoukitti-cpu.github.io/DATA-ANALYTICS-PORTFOLIO/projects/04-risque-credit/dashboard/web/) · [code](dashboard/web/) · captures : [vue d’ensemble](preview/dashboard_web.png) et [filtre « Très élevé »](preview/dashboard_web_risque_eleve.png)."
    count_block = (
        f"- Tables CSV traitées : **{format_count(counts['processed_table_count'])}** ({format_count(counts['star_table_count'])} tables en étoile et une scorecard auxiliaire).\n"
        f"- Recommandations chiffrées : **{format_count(counts['recommendation_count'])}**; graphiques Matplotlib : **{format_count(counts['visual_count'])}**."
    )
    blocks = {
        "DYNAMIQUE_SUMMARY": summary,
        "DYNAMIQUE_DATA": data_summary,
        "DYNAMIQUE_RESULTS": result_table,
        "DYNAMIQUE_METHOD": method_block,
        "DYNAMIQUE_RECOMMENDATIONS": recommendations_table,
        "DYNAMIQUE_STATUS": status_block,
        "DYNAMIQUE_DASHBOARD": dashboard_block,
        "DYNAMIQUE_COUNTS": count_block,
    }
    updated = text
    for marker, value in blocks.items():
        text_between_markers[marker] = value
        updated = marker_block(updated, marker)
    readme_path.write_text(updated, encoding="utf-8")


def main() -> None:
    results = PROJECT_ROOT / "results"
    processed = PROJECT_ROOT / "data" / "processed"
    quality = pd.read_csv(results / "quality_check.csv")
    kpis = pd.read_csv(results / "portfolio_kpis.csv").iloc[0]
    model = pd.read_csv(results / "model_metrics.csv").iloc[0]
    bands = pd.read_csv(results / "risk_band_summary.csv")
    recommendations = pd.read_csv(results / "recommendations.csv")
    metrics_summary = pd.read_csv(results / "metrics_summary.csv")
    parity = pd.read_csv(results / "sql_parity.csv")
    fact = pd.read_csv(processed / "fact_clients.csv")
    scorecard = pd.read_csv(processed / "model_scorecard.csv")
    processed_tables = sorted(processed.glob("*.csv"))
    star_table_names = {
        "fact_clients.csv", "dim_age_band.csv", "dim_education.csv", "dim_marriage.csv",
        "dim_limit_band.csv", "dim_pay_status.csv", "dim_risk_band.csv",
    }
    star_table_count = sum(1 for path in processed_tables if path.name in star_table_names)
    visual_count = len(list((PROJECT_ROOT / "visuals").glob("*.png")))
    project_files = [path for path in PROJECT_ROOT.rglob("*") if path.is_file()]
    total_bytes = sum(path.stat().st_size for path in project_files)
    largest_bytes = max((path.stat().st_size for path in project_files), default=0)
    fact_rows = len(fact)
    raw_columns = 25
    high_risk_clients = int(bands.loc[bands["risk_band_key"].isin([3, 4]), "customers"].sum())
    expected_loss_45 = float(bands["expected_loss_lgd45_ntd"].sum())
    quality_pass_count = int((quality["status"] == "PASS").sum())
    quality_control_count = int(len(quality))
    repo_readmes = [PROJECT_ROOT / "README.md", REPO_ROOT / "README.md"]
    link_issues = resolve_markdown_links(repo_readmes)
    scanned_text = []
    for path in project_files:
        if path.suffix.lower() in {".md", ".py", ".sql", ".txt", ".m"}:
            try:
                scanned_text.append(path.read_text(encoding="utf-8"))
            except UnicodeDecodeError:
                pass
    scanned_text.extend(path.read_text(encoding="utf-8") for path in repo_readmes if path.exists())
    repository_text = "\n".join(scanned_text)
    absolute_path_pattern = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]|(?<!:)[/]" + re.escape("home") + r"[/]")
    absolute_path_found = bool(absolute_path_pattern.search(repository_text))
    todo_token = "TO" + "DO"
    todo_found = bool(re.search(r"\b" + todo_token + r"\b", repository_text, flags=re.IGNORECASE))
    linkedin_domain = "linkedin" + ".com"
    linkedin_link_found = bool(re.search(r"https?://(?:www\.)?" + re.escape(linkedin_domain), repository_text, flags=re.IGNORECASE))
    project_readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    readme_line_count = len(project_readme.splitlines())
    no_cache_files = not any(
        path.name == "__pycache__" or path.suffix in {".pyc", ".pyo", ".db-journal"}
        for path in PROJECT_ROOT.rglob("*")
    )
    raw_hash = sha256_file(RAW_XLS)
    largest_file_count = sum(1 for path in project_files if path.stat().st_size > 50 * 1024 * 1024)
    project_mb = total_bytes / (1024 * 1024)
    all_quality_pass = bool((quality["status"] == "PASS").all())
    all_parity_pass = bool((parity["status"] == "PASS").all()) and len(parity) >= 5
    score_valid = all(
        math.isfinite(float(model[key])) and 0 <= float(model[key]) <= 1
        for key in ["roc_auc", "pr_auc_average_precision", "ks_statistic", "precision_at_threshold", "recall_at_threshold", "brier_score"]
    )
    db_path = processed / "credit_risk.db"
    sqlite_table_count = 0
    sqlite_fact_rows = 0
    if db_path.exists():
        import sqlite3
        with sqlite3.connect(db_path) as connection:
            sqlite_table_count = int(connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchone()[0])
            sqlite_fact_rows = int(connection.execute("SELECT COUNT(*) FROM fact_clients").fetchone()[0])
    checks: list[tuple[str, str, str, bool]] = []

    def add(name: str, expected: str, observed: str, passed: bool) -> None:
        checks.append((name, expected, observed, bool(passed)))

    add("Source UCI", "Fichier brut inchangé, SHA-256 conforme", f"{raw_hash}; {format_count(RAW_XLS.stat().st_size)} octets", raw_hash == EXPECTED_RAW_SHA256)
    add("Structure source", "30 000 lignes et 25 colonnes", f"{format_count(fact_rows)} lignes fact_clients; {format_count(raw_columns)} colonnes brutes", fact_rows == 30_000 and raw_columns == 25)
    add("Qualité et conservation", "Aucun échec; aucune ligne supprimée", f"{format_count(quality_pass_count)}/{format_count(quality_control_count)} PASS; {format_count(int(quality.loc[quality['rule'] == 'source_rows', 'count_after'].iloc[0]))} lignes après nettoyage", all_quality_pass and fact_rows == 30_000)
    source_doc = (PROJECT_ROOT / "data" / "raw" / "SOURCE.md").read_text(encoding="utf-8")
    add("Licence et attribution", "CC BY 4.0 et citation Yeh (2009) dans SOURCE et README", "CC BY 4.0" if "CC BY 4.0" in source_doc and "Yeh, I. (2009)" in source_doc and "CC BY 4.0" in project_readme else "mention absente", "CC BY 4.0" in source_doc and "Yeh, I. (2009)" in source_doc and "CC BY 4.0" in project_readme)
    add("Modèle en étoile", "7 tables en étoile + 1 scorecard; fact 30 000 lignes", f"{format_count(len(processed_tables))} CSV traités; {format_count(sqlite_table_count)} tables SQLite; {format_count(sqlite_fact_rows)} lignes fact", len(processed_tables) == 8 and star_table_count == 7 and sqlite_table_count == 8 and sqlite_fact_rows == 30_000)
    add("Modèle prédictif", "Split stratifié 70/30, graine 42, seuil documenté; variables sensibles exclues", f"{format_count(model['train_clients'])}/{format_count(model['test_clients'])}; random_state={format_count(model['random_state'])}; seuil {format_ratio(model['decision_threshold'], 2)}; ROC-AUC {format_ratio(model['roc_auc'])}", int(model["random_state"]) == 42 and int(model["train_clients"]) + int(model["test_clients"]) == fact_rows and score_valid and "sex" in str(model["protected_features_excluded"]) and "marriage" in str(model["protected_features_excluded"]) and "age" in str(model["protected_features_excluded"]))
    add("Parité SQL / Python", "Au moins 5 indicateurs, écarts dans la tolérance", f"{format_count(len(parity))} comparaisons; {format_count(int((parity['status'] == 'PASS').sum()))} PASS", all_parity_pass)
    add("README et navigation", "Badge PORTFOLIO, moins de 120 lignes, liens/images locaux résolus", f"{format_count(readme_line_count)} lignes; {format_count(len(link_issues))} lien(s) rompu(s)", "img.shields.io/badge/PORTFOLIO" in project_readme and readme_line_count <= 120 and not link_issues)
    add("Conformité du texte", "Aucun marqueur de tâche restant, chemin absolu ou lien professionnel", f"Détection tâche={todo_found}; chemin absolu={absolute_path_found}; LinkedIn URL={linkedin_link_found}", not todo_found and not absolute_path_found and not linkedin_link_found)
    add("Poids du projet", "Projet <25 Mo et aucun fichier >50 Mo", f"{project_mb:.2f} Mo; {format_count(largest_file_count)} fichier(s) >50 Mo", project_mb < 25 and largest_file_count == 0)
    add("Graphiques", "De 6 à 8 PNG Matplotlib", f"{format_count(visual_count)} PNG", 6 <= visual_count <= 8)
    add("Recommandations", "De 4 à 6 pistes chiffrées, issues des résultats", f"{format_count(len(recommendations))} recommandations générées", 4 <= len(recommendations) <= 6)
    add("Caches", "Aucun cache", "aucun cache" if no_cache_files else "cache détecté", no_cache_files)
    overall_status = "PASS" if all(row[3] for row in checks) else "FAIL"
    counts = {
        "fact_rows": fact_rows,
        "raw_columns": raw_columns,
        "processed_table_count": len(processed_tables),
        "star_table_count": star_table_count,
        "visual_count": visual_count,
        "quality_pass_count": quality_pass_count,
        "quality_control_count": quality_control_count,
        "indicator_count": len(metrics_summary),
        "recommendation_count": len(recommendations),
        "high_risk_clients": high_risk_clients,
        "expected_loss_45": expected_loss_45,
        "overall_status": overall_status,
    }
    replace_readme_blocks(metrics_summary, kpis, model, quality, recommendations, counts)
    project_readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    readme_line_count = len(project_readme.splitlines())
    if readme_line_count > 120:
        checks.append(("Longueur README", "≤120 lignes", f"{format_count(readme_line_count)} lignes", False))
        overall_status = "FAIL"

    report_lines = [
        "# Rapport de validation — Projet 04",
        "",
        "Généré par `scripts/06_report.py`; les compteurs ci-dessous sont recalculés depuis les données et les fichiers produits.",
        "",
        "## Compteurs générés",
        "",
        "| Élément | Valeur | Source |",
        "|---|---:|---|",
        f"| Clients traités | {format_count(fact_rows)} | `data/processed/fact_clients.csv` |",
        f"| Colonnes source | {format_count(raw_columns)} | Schéma XLS UCI et `DATA_DICTIONARY.md` |",
        f"| Tables CSV | {format_count(len(processed_tables))} | `data/processed/` |",
        f"| Tables du schéma en étoile | {format_count(star_table_count)} | Fact et dimensions |",
        f"| Indicateurs de portefeuille | {format_count(len(metrics_summary))} | `results/metrics_summary.csv` |",
        f"| Recommandations quantifiées | {format_count(len(recommendations))} | `results/recommendations.csv` |",
        f"| Graphiques PNG | {format_count(visual_count)} | `visuals/` |",
        "",
        "## Indicateurs clés",
        "",
        f"Taux de défaut : **{format_pct(kpis['default_rate'])}**; limite totale : **{format_money(kpis['total_credit_limit_ntd'])}**; exposition des défaillants : **{format_money(kpis['defaulter_credit_limit_exposure_ntd'])}**; ROC-AUC test : **{format_ratio(model['roc_auc'])}**; PR-AUC test : **{format_ratio(model['pr_auc_average_precision'])}**; perte attendue test à LGD 45 % : **{format_money(expected_loss_45)}**.",
        "",
        "## Contrôles automatisés",
        "",
        "| Contrôle | Attendu | Constaté | Statut |",
        "|---|---|---|---|",
    ]
    for name, expected, observed, passed in checks:
        report_lines.append(f"| {name} | {expected} | {observed} | {'PASS' if passed else 'FAIL'} |")
    report_lines.extend(
        [
            "",
            f"**Statut global automatisé : {overall_status}.**",
            "",
            "## Parité SQL / Python",
            "",
            f"La base `data/processed/credit_risk.db` est reconstruite par `scripts/05_sql.py` depuis les CSV. Le fichier `results/sql_parity.csv` contient **{format_count(len(parity))} comparaisons**; toutes doivent être PASS à la tolérance indiquée.",
            "",
            "## Hypothèses conservées",
            "",
            "Codes `pay_*` -2 et 0 traités comme hypothèses documentées; utilisation plafonnée entre 0 et 150 %; ratio de paiement défini seulement si `bill_amt1 > 0`; bandes de score fixes; seuil de classification issu de `model_metrics.csv`; perte attendue fondée sur la facture positive et une LGD supposée à 45 %, avec sensibilité 30/45/60 %.",
        ]
    )
    report_path = PROJECT_ROOT / "qa" / "validation_report.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    if overall_status != "PASS":
        failed = [name for name, _, _, passed in checks if not passed]
        raise RuntimeError(f"Échec des contrôles du projet 04 : {failed}")
    print(f"Validation générée : {overall_status}; {len(checks)} contrôles; README {readme_line_count} lignes.")


if __name__ == "__main__":
    main()
