"""Génère le rapport QA, les valeurs attendues DAX et les résumés des README."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

import pandas as pd

from pipeline_utils import ROOT, population_values

REPO = ROOT.parents[1]
RAW_FULL = ROOT / "data/raw/openml_43627_full.parquet"
PROCESSED_TABLES = [
    "dim_outcome.csv", "dim_amount_band.csv", "dim_time_window.csv", "fact_transactions.csv",
    "fact_model_test.csv", "model_scorecard.csv", "model_cost_sensitivity.csv", "model_money_controls.csv",
]
MAX_PROJECT_BYTES = 25_000_000
MAX_FILE_BYTES = 50_000_000


def fr_num(value: float, digits: int = 0) -> str:
    return f"{float(value):,.{digits}f}".replace(",", " ").replace(".", ",")


def fr_pct(value: float, digits: int = 3) -> str:
    return f"{float(value) * 100:.{digits}f}".replace(".", ",") + " %"


def replace_block(text: str, start: str, end: str, content: str) -> str:
    if start not in text or end not in text:
        raise ValueError(f"Marqueurs absents: {start} / {end}")
    left = text.index(start) + len(start)
    right = text.index(end, left)
    return text[:left] + "\n" + content.rstrip() + "\n" + text[right:]


def local_markdown_targets(path: Path, text: str) -> list[str]:
    targets = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text)
    targets += re.findall(r"(?:href|src)=[\"']([^\"']+)[\"']", text, flags=re.IGNORECASE)
    local = []
    for target in targets:
        target = target.strip().strip("<>")
        if not target or target.startswith(("http://", "https://", "mailto:", "data:", "#")):
            continue
        target_path = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if target_path:
            local.append(target_path)
    return local


def broken_links(paths: list[Path]) -> list[str]:
    broken = []
    for markdown in paths:
        text = markdown.read_text(encoding="utf-8")
        for target in local_markdown_targets(markdown, text):
            if not (markdown.parent / target).exists():
                broken.append(f"{markdown.relative_to(REPO)} -> {target}")
    return broken


def project_files() -> list[Path]:
    return [p for p in ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p != RAW_FULL]


def render_dax_expected(overall: pd.Series, model: pd.Series, money: pd.Series) -> str:
    values = [
        ("M01", "Transactions estimées", fr_num(overall["transactions_population_exact"])),
        ("M02", "Fraudes estimées", fr_num(overall["fraud_transactions_population_exact"])),
        ("M03", "Taux de fraude pondéré", fr_pct(overall["fraud_rate_population_exact"])),
        ("M04", "Montant estimé", fr_num(overall["amount_total_weighted_sample"], 2) + " unités du dataset"),
        ("M05", "Exposition fraude estimée", fr_num(overall["fraud_amount_weighted_sample"], 2) + " unités du dataset"),
        ("M06", "Transactions test estimées", fr_num(model["test_transactions_population_estimate"])),
        ("M07", "Transactions signalées modèle", fr_num(money["transactions_flagged_estimate"], 2)),
        ("M08", "Précision test pondérée", fr_pct(model["precision_weighted"], 2)),
        ("M09", "Rappel test pondéré", fr_pct(model["recall_weighted"], 2)),
        ("M10", "F1 test pondéré", fr_pct(model["f1_weighted"], 2)),
        ("M11", "PR-AUC test", f"{float(model['pr_auc_weighted']):.4f}"),
        ("M12", "Seuil recommandé", f"{float(model['decision_threshold']):.3f}"),
        ("M13", "Exposition fraude interceptée", fr_num(money["fraud_amount_intercepted_estimate"], 2) + " unités du dataset"),
        ("M14", "Exposition fraude manquée", fr_num(money["fraud_amount_missed_estimate"], 2) + " unités du dataset"),
        ("M15", "Coût prévu modèle", fr_num(money["expected_cost_estimate"], 2) + " unités du dataset"),
    ]
    return "\n".join([
        "| ID | Mesure | Valeur attendue depuis les sorties générées |",
        "|---|---|---|",
        *[f"| {key} | {name} | {value} |" for key, name, value in values],
    ])


def main() -> None:
    values = population_values()
    results = ROOT / "results"
    processed = ROOT / "data/processed"
    sample = pd.read_parquet(processed / "transactions_sample.parquet")
    quality = pd.read_csv(results / "quality_check.csv")
    split = pd.read_csv(results / "split_validation.csv", dtype={"value": str}).set_index("metric")
    parity = pd.read_csv(results / "sql_parity.csv")
    metrics = pd.read_csv(results / "model_metrics.csv").set_index("method")
    money = pd.read_csv(results / "money_controls.csv").set_index("method")
    overall = pd.read_csv(results / "overall_kpis.csv").set_index("metric")["value"]
    recommendations = pd.read_csv(results / "recommendations.csv")
    dax_path = ROOT / "model/DAX_MEASURES.md"
    readme_path = ROOT / "README.md"
    dax_text = dax_path.read_text(encoding="utf-8")
    readme_text = readme_path.read_text(encoding="utf-8")

    dax_count = len(re.findall(r"(?m)^### M\d{2} ·", dax_text))
    page_plan_text = (ROOT / "powerbi/PAGE_PLAN.md").read_text(encoding="utf-8")
    page_count = len(re.findall(r"(?m)^### Page \d+ ·", page_plan_text))
    table_count = sum((processed / name).is_file() for name in PROCESSED_TABLES)
    visual_count = len(list((ROOT / "visuals").glob("*.png")))
    sql_queries = len([p for p in (ROOT / "sql").glob("[0-9][0-9]_*.sql")])
    metrics_model = metrics.loc["Modèle logistique"]
    metrics_baseline = metrics.loc["Règle montant P99"]
    money_model = money.loc["Modèle logistique"]
    money_baseline = money.loc["Règle montant P99"]
    source_total = float(values["transactions_total"])
    source_fraud = float(values["transactions_fraud"])
    sample_total = int(len(sample))
    sample_fraud = int(sample["Class"].eq(1).sum())
    weighted_total = float(sample["sampling_weight"].sum())
    weight_error = abs(weighted_total - source_total)
    quality_failures = int(quality["status"].eq("FAIL").sum())
    sql_passes = int(parity["status"].eq("PASS").sum())
    sql_failures = int(parity["status"].eq("FAIL").sum())
    split_failures = int(split["status"].ne("PASS").sum())
    duplicate_crossing = int(float(split.loc["duplicate_groups_crossing_partitions", "value"]))
    test_fraction = float(split.loc["test_fraction", "value"])
    manual_text = (ROOT / "qa/CHECKLIST.md").read_text(encoding="utf-8")
    manual_marks = re.findall(r"(?m)^- \[([ xX])\]", manual_text)
    manual_all_unchecked = bool(manual_marks) and all(mark == " " for mark in manual_marks)

    files = project_files()
    total_bytes = sum(path.stat().st_size for path in files)
    largest_bytes = max((path.stat().st_size for path in files), default=0)
    over_50mb = [path for path in files if path.stat().st_size > MAX_FILE_BYTES]
    caches = [p for p in ROOT.rglob("*") if p.is_file() and (p.suffix == ".pyc" or "__pycache__" in p.parts or ".ipynb_checkpoints" in p.parts)]
    raw_ignore = subprocess.run(["git", "-C", str(REPO), "check-ignore", "--quiet", "projects/05-fraude-bancaire/data/raw/openml_43627_full.parquet"], check=False).returncode == 0
    required = [
        "README.md", "requirements.txt", "data/raw/SOURCE.md", "data/raw/DATA_DICTIONARY.md",
        "data/processed/transactions_sample.parquet", "data/processed/fraud_controls.db",
        "sql/schema.sql", "scripts/00_make_sample.py", "scripts/01_clean.py", "scripts/02_analyze.py",
        "scripts/03_model.py", "scripts/04_scorecard.py", "scripts/05_sql.py", "scripts/06_report.py",
        "scripts/run_all.py", "scripts/pipeline_utils.py", "results/population_kpis.csv",
        "results/quality_check.csv", "results/split_validation.csv", "results/sql_parity.csv",
        "model/DATA_MODEL.md", "model/DAX_MEASURES.md", "powerbi/PAGE_PLAN.md",
        "powerbi/POWER_QUERY.md", "powerbi/EXPORT_PREVIEWS.md", "qa/CHECKLIST.md",
        "qa/INTERACTION_TESTS.md",
    ]
    missing_files = [name for name in required if not (ROOT / name).is_file()]

    # Generate value tables and summary blocks from results; README numbers are not manually entered.
    model_rate = float(values["fraud_rate"])
    summary = "\n".join([
        f"- **Population source :** {fr_num(source_total)} transactions, {fr_num(source_fraud)} fraudes ({fr_pct(model_rate)}); échantillon pondéré de {fr_num(sample_total)} lignes.",
        f"- **Modèle (test) :** PR-AUC {float(metrics_model['pr_auc_weighted']):.4f}, précision {fr_pct(metrics_model['precision_weighted'], 2)}, rappel {fr_pct(metrics_model['recall_weighted'], 2)}, seuil {float(metrics_model['decision_threshold']):.3f} choisi hors test.",
        f"- **Comparaison sous hypothèses :** coût estimé {fr_num(money_model['expected_cost_estimate'])} contre {fr_num(money_baseline['expected_cost_estimate'])} unités pour la règle de montant; exposition fraude interceptée {fr_num(money_model['fraud_amount_intercepted_estimate'])} unités.",
        f"- **Livrables automatisés :** {table_count} tables Power BI, {dax_count} mesures DAX, {page_count} pages planifiées, {visual_count} graphiques, {sql_passes}/{len(parity)} comparaisons SQL/Python; dashboard manuel à construire.",
    ])
    key_results = "\n".join([
        "| Indicateur | Résultat | Référence |",
        "|---|---|---|",
        f"| Fraude source | {fr_pct(model_rate)} ({fr_num(source_fraud)} / {fr_num(source_total)}) | `results/population_kpis.csv` |",
        f"| Modèle logistique | PR-AUC {float(metrics_model['pr_auc_weighted']):.4f}; précision {fr_pct(metrics_model['precision_weighted'],2)}; rappel {fr_pct(metrics_model['recall_weighted'],2)} | `results/model_metrics.csv` |",
        f"| Règle montant P99 | rappel {fr_pct(metrics_baseline['recall_weighted'],2)}; coût {fr_num(money_baseline['expected_cost_estimate'])} unités | `results/model_metrics.csv`; `results/money_controls.csv` |",
        f"| Modèle, coût proxy | seuil {float(metrics_model['decision_threshold']):.3f}; coût {fr_num(money_model['expected_cost_estimate'])} unités | `results/money_controls.csv`; `results/cost_assumptions.csv` |",
        f"| Parité SQL/Python | {sql_passes}/{len(parity)} PASS | `results/sql_parity.csv` |",
    ])
    recommendation_md = "\n".join([
        "| Priorité | Recommandation | Évidence calculée |",
        "|---:|---|---|",
        *[f"| {int(row.priority)} | {str(row.recommendation).replace('|', '/')} | {str(row.evidence).replace('|', '/')} |" for row in recommendations.itertuples(index=False)],
    ])
    dax_expected = render_dax_expected(overall, metrics_model, money_model)
    dax_text = replace_block(dax_text, "<!-- AUTO:DAX_EXPECTED_BEGIN -->", "<!-- AUTO:DAX_EXPECTED_END -->", dax_expected)
    dax_path.write_text(dax_text, encoding="utf-8")

    project_status_placeholder = "EN COURS"
    readme_text = replace_block(readme_text, "<!-- AUTO:SUMMARY_BEGIN -->", "<!-- AUTO:SUMMARY_END -->", summary)
    readme_text = replace_block(readme_text, "<!-- AUTO:KEY_RESULTS_BEGIN -->", "<!-- AUTO:KEY_RESULTS_END -->", key_results)
    readme_text = replace_block(readme_text, "<!-- AUTO:RECOMMENDATIONS_BEGIN -->", "<!-- AUTO:RECOMMENDATIONS_END -->", recommendation_md)
    readme_text = readme_text.replace("{{AUTO_QA_STATUS}}", project_status_placeholder)
    readme_path.write_text(readme_text, encoding="utf-8")

    # Update only the project 05 root-index row and its generated deliverables table.
    root_readme_path = REPO / "README.md"
    root_readme = root_readme_path.read_text(encoding="utf-8")
    root_row = (
        f"| 05 | [Détection de fraude sur les transactions bancaires](projects/05-fraude-bancaire/README.md) | "
        f"Prioriser la revue; fraude source : **{fr_pct(model_rate)}**. | Python · pandas · scikit-learn · SQLite · Power BI/DAX | "
        f"Analyse terminée; dashboard à construire par Samuel |"
    )
    row_pattern = re.compile(r"(?m)^\| 05 \| \[Détection de fraude sur les transactions bancaires\].*$")
    root_readme, row_count = row_pattern.subn(root_row, root_readme, count=1)
    if row_count != 1:
        raise SystemExit("Ligne projet 05 absente du README racine; ajouter la ligne d'index avant run_all.py.")
    root_status = "\n".join([
        "| Données | Qualité | SQL/Python | DAX | Rapport QA | Dashboard Power BI |",
        "|---|---|---|---|---|---|",
        f"| Échantillon {fr_num(sample_total)} lignes | {project_status_placeholder} | {sql_passes}/{len(parity)} comparaisons | {dax_count} mesures | {project_status_placeholder} | À construire par Samuel |",
    ])
    root_readme = replace_block(root_readme, "<!-- AUTO:PROJECT05_STATUS_BEGIN -->", "<!-- AUTO:PROJECT05_STATUS_END -->", root_status)
    root_readme_path.write_text(root_readme, encoding="utf-8")

    (ROOT / "qa/validation_report.md").write_text("# Rapport de validation automatique — projet 05\n\nGénération en cours par `scripts/06_report.py`.\n", encoding="utf-8")

    # Local Markdown links/images are checked after all generated documentation exists.
    docs_to_check = [*ROOT.rglob("*.md"), root_readme_path]
    docs_to_check.extend([REPO / "docs/ROADMAP.md"])
    link_errors = broken_links(docs_to_check)
    line_count = len(readme_path.read_text(encoding="utf-8").splitlines())
    text_extensions = {".md", ".py", ".sql", ".txt", ".csv"}
    # Exclude this validator and its generated report: their rule names would otherwise
    # self-trigger the TODO/LinkedIn scans on every clean repository run.
    self_referential = {ROOT / "scripts/06_report.py", ROOT / "qa/validation_report.md"}
    text_files = [p for p in project_files() if p.suffix.lower() in text_extensions and p not in self_referential]
    all_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in text_files)
    absolute_paths = re.findall(r"(?:^|[\s`(\"'])/(?:home|Users|tmp)/[^\s`\"')]+|\b[A-Za-z]:\\[^\s`\"')]+", all_text)
    todos = len(re.findall(r"\bTODO\b", all_text, flags=re.IGNORECASE))
    linked_in = len(re.findall(r"linkedin", all_text, flags=re.IGNORECASE))
    emoji = len(re.findall(r"[\U0001F000-\U0001FAFF\U00002600-\U000027BF]", all_text))
    markdown_badge = "![PORTFOLIO](https://img.shields.io/badge/PORTFOLIO" in readme_path.read_text(encoding="utf-8")
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    pinned = bool(requirements) and all("==" in line for line in requirements if line.strip())
    forbidden = [p.name for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in {".html", ".xlsx", ".xls", ".pbix", ".pbip", ".pbir", ".tmdl"}]

    checks = []
    def record(label: str, expected: str, observed: str, ok: bool) -> None:
        checks.append({"label": label, "expected": expected, "observed": observed, "status": "PASS" if ok else "FAIL"})

    record("Fichiers requis", "Tous présents", f"{len(missing_files)} absent(s)", not missing_files)
    record("Échantillon et fraudes", f"{int(source_total):,} source; {int(source_fraud):,} fraudes conservées", f"{sample_total:,} échantillon; {sample_fraud:,} fraudes", sample_fraud == int(source_fraud) and sample_total == int(float(values["sample_rows"])))
    record("Poids populationnels", "Reconstruction à moins de 0,01 transaction", f"écart {weight_error:.10f}", weight_error < 0.01)
    record("Contrôles qualité", "Aucun FAIL; informations de doublons documentées", f"{quality_failures} FAIL; {len(quality)} règles", quality_failures == 0)
    record("Split et fuite de doublons", "Test 30 % ± 0,5 %; aucun groupe partagé", f"test {test_fraction:.4%}; groupes partagés {duplicate_crossing}; échecs {split_failures}", abs(test_fraction - .30) <= .005 and duplicate_crossing == 0 and split_failures == 0)
    record("Parité SQL/Python", "Au moins 5, tous PASS", f"{sql_passes}/{len(parity)} PASS; {sql_failures} FAIL", len(parity) >= 5 and sql_failures == 0 and sql_passes == len(parity))
    record("Tables Power BI", "8 CSV traités", f"{table_count}/8 présents", table_count == 8)
    record("Mesures DAX", "Définitions numérotées et valeurs générées", f"{dax_count} mesures", dax_count == 15)
    record("Pages planifiées", "4 pages", f"{page_count} pages", page_count == 4)
    record("Graphiques", "Au moins 6 PNG Matplotlib", f"{visual_count} PNG", visual_count >= 6)
    record("README projet", "Au plus 120 lignes; badge PORTFOLIO", f"{line_count} lignes; badge {'présent' if markdown_badge else 'absent'}", line_count <= 120 and markdown_badge)
    record("Liens relatifs/images", "Tous résolus", f"{len(link_errors)} cassé(s)", len(link_errors) == 0)
    record("Taille du projet", "<25 Mo hors Parquet complet local", f"{total_bytes/1_000_000:.2f} Mo; maximum {largest_bytes/1_000_000:.2f} Mo", total_bytes < MAX_PROJECT_BYTES and not over_50mb)
    record("Parquet complet ignoré", "Exclu de Git et du décompte versionné", "ignore actif" if raw_ignore else "règle d'exclusion absente", raw_ignore)
    record("Caches Python", "Aucun", f"{len(caches)} artefact(s)", len(caches) == 0)
    record("Conformité texte", "Aucun chemin absolu, TODO, LinkedIn ou emoji", f"{len(absolute_paths)} chemin(s), {todos} TODO, {linked_in} LinkedIn, {emoji} emoji", not absolute_paths and todos == 0 and linked_in == 0 and emoji == 0)
    record("Dépendances", "Versions directes épinglées avec ==", f"{len(requirements)} dépendances", pinned)
    record("Formats interdits", "Aucun HTML/Excel/PBIX/PBIP/PBIR/TMDL", f"{len(forbidden)} fichier(s)", not forbidden)
    record("Checklist Desktop", "Tous les tests manuels restent non cochés", f"{len(manual_marks)} cases; toutes non cochées={manual_all_unchecked}", manual_all_unchecked)

    overall_status = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    readme_text = readme_path.read_text(encoding="utf-8").replace("EN COURS", overall_status)
    readme_path.write_text(readme_text, encoding="utf-8")
    root_readme = root_readme_path.read_text(encoding="utf-8").replace("EN COURS", overall_status)
    root_readme_path.write_text(root_readme, encoding="utf-8")

    report = [
        "# Rapport de validation automatique — projet 05",
        "",
        f"**Statut automatisé : {overall_status}.** Généré par `scripts/06_report.py` depuis les sorties du pipeline. Les tests Desktop sont séparés et restent à faire par Samuel.",
        "",
        "| Contrôle | Attendu | Constaté | Statut |",
        "|---|---|---|---|",
        *[f"| {item['label']} | {item['expected']} | {item['observed']} | {item['status']} |" for item in checks],
        "",
        f"**Source :** OpenML 43627; SHA-256 `{values['source_sha256']}`; {int(float(values['source_size_bytes'])):,} octets; le fichier complet local est ignoré par Git.",
        f"**Référence modèle :** seuil {float(metrics_model['decision_threshold']):.3f} choisi sur prédictions hors pli du train; test {test_fraction:.2%}; PR-AUC pondérée {float(metrics_model['pr_auc_weighted']):.4f}; précision {float(metrics_model['precision_weighted']):.4%}; rappel {float(metrics_model['recall_weighted']):.4%}.",
        f"**Coûts :** hypothèses de base sévérité={float(money_model['missed_fraud_loss_severity_assumption']):.1f}, friction={float(money_model['legitimate_friction_cost_assumption']):.1f} unités; le modèle et la référence P99 ne représentent pas des pertes comptables constatées.",
        "**Manuel :** le dashboard Power BI, les mesures saisies dans Desktop, les scénarios d’interaction et les exports PDF/PNG ne sont pas exécutés dans cette livraison.",
    ]
    (ROOT / "qa/validation_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    # The validation report now exists; verify generated relative links once more.
    final_link_errors = broken_links([*ROOT.rglob("*.md"), root_readme_path, REPO / "docs/ROADMAP.md"])
    if final_link_errors:
        raise SystemExit("Lien(s) cassé(s) après génération: " + "; ".join(final_link_errors))
    print(f"Rapport QA {overall_status}: {len(checks)} contrôles; {sql_passes}/{len(parity)} parités SQL; {table_count} tables, {dax_count} mesures, {page_count} pages planifiées.")
    if overall_status != "PASS":
        raise SystemExit("Au moins un contrôle QA est en échec; consulter qa/validation_report.md.")


if __name__ == "__main__":
    main()
