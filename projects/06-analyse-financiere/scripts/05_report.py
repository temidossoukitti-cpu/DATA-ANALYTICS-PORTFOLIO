"""Génère le rapport QA, les valeurs attendues DAX et les blocs dynamiques des README."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from urllib.parse import unquote

import pandas as pd

from pipeline_utils import ROOT, fr_num, fr_pct, fr_ratio

REPO = ROOT.parents[1]
RAW = ROOT / "data/raw/mastercard_companyfacts.json"
RAW_SHA256 = "eec2f64179fe268380a6f9f4b5e3da53a9c1c5adb988aa31cc40c8372c0d8899"
RAW_BYTES = 4_182_087
PROCESSED_TABLES = [
    "dim_fiscal_year.csv", "dim_metric.csv", "dim_ratio.csv", "fact_financials.csv",
    "fact_ratios.csv", "financial_scorecard.csv", "financial_alerts.csv",
]
MAX_PROJECT_BYTES = 25_000_000
MAX_FILE_BYTES = 50_000_000


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
    return [p for p in ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts]


def render_dax_expected(latest: pd.Series) -> str:
    values = [
        ("M01", "Produits", fr_num(latest["revenue"]) + " USD"),
        ("M02", "Résultat d'exploitation", fr_num(latest["operating_income"]) + " USD"),
        ("M03", "Résultat net", fr_num(latest["net_income"]) + " USD"),
        ("M04", "Marge opérationnelle", fr_pct(latest["operating_margin"], 2)),
        ("M05", "Marge nette", fr_pct(latest["net_margin"], 2)),
        ("M06", "ROE", fr_pct(latest["roe"], 2)),
        ("M07", "ROA", fr_pct(latest["roa"], 2)),
        ("M08", "Flux de trésorerie disponible", fr_num(latest["fcf"]) + " USD"),
        ("M09", "Marge de flux disponible", fr_pct(latest["fcf_margin"], 2)),
        ("M10", "Croissance des produits", fr_pct(latest["revenue_growth"], 2)),
        ("M11", "Ratio de liquidité courante", fr_ratio(latest["current_ratio"], 2)),
        ("M12", "Taux d'endettement", fr_pct(latest["debt_ratio"], 2)),
        ("M13", "Couverture des intérêts", fr_ratio(latest["interest_coverage"], 2) + "x"),
        ("M14", "BPA dilué", fr_num(latest["eps_diluted"], 2) + " USD par action"),
        ("M15", "Taux d'imposition effectif", fr_pct(latest["effective_tax_rate"], 2)),
    ]
    return "\n".join([
        "| ID | Mesure | Valeur attendue depuis les sorties générées |",
        "|---|---|---|",
        *[f"| {key} | {name} | {value} |" for key, name, value in values],
    ])


def main() -> None:
    results = ROOT / "results"
    processed = ROOT / "data/processed"
    quality = pd.read_csv(results / "quality_check.csv")
    parity = pd.read_csv(results / "sql_parity.csv")
    annual = pd.read_csv(results / "annual_kpis.csv").set_index("fiscal_year")
    scorecard = pd.read_csv(results / "financial_scorecard.csv").iloc[0]
    summary = pd.read_csv(results / "ratio_summary.csv").set_index("ratio_key")
    growth = pd.read_csv(results / "growth_summary.csv").set_index("metric")
    recommendations = pd.read_csv(results / "recommendations.csv")
    latest_year = int(annual.index.max())
    prior_year = int(latest_year - 1)
    latest = annual.loc[latest_year]

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
    quality_failures = int(quality["status"].eq("FAIL").sum())
    sql_passes = int(parity["status"].eq("PASS").sum())
    sql_failures = int(parity["status"].eq("FAIL").sum())
    manual_text = (ROOT / "qa/CHECKLIST.md").read_text(encoding="utf-8")
    manual_marks = re.findall(r"(?m)^- \[([ xX])\]", manual_text)
    manual_all_unchecked = bool(manual_marks) and all(mark == " " for mark in manual_marks)

    files = project_files()
    total_bytes = sum(path.stat().st_size for path in files)
    largest_bytes = max((path.stat().st_size for path in files), default=0)
    over_50mb = [path for path in files if path.stat().st_size > MAX_FILE_BYTES]
    caches = [p for p in ROOT.rglob("*") if p.is_file() and (p.suffix == ".pyc" or "__pycache__" in p.parts or ".ipynb_checkpoints" in p.parts)]
    raw_hash = hashlib.sha256(RAW.read_bytes()).hexdigest()
    raw_ok = raw_hash == RAW_SHA256 and RAW.stat().st_size == RAW_BYTES
    required = [
        "README.md", "requirements.txt", "data/raw/SOURCE.md", "data/raw/DATA_DICTIONARY.md",
        "data/raw/mastercard_companyfacts.json", "data/processed/mastercard_financials.db",
        "sql/schema.sql", "scripts/01_clean.py", "scripts/02_analyze.py", "scripts/03_ratios.py",
        "scripts/04_sql.py", "scripts/05_report.py", "scripts/run_all.py", "scripts/pipeline_utils.py",
        "results/quality_check.csv", "results/financial_scorecard.csv", "results/annual_kpis.csv",
        "results/ratio_summary.csv", "results/growth_summary.csv", "results/reference_comparison.csv",
        "results/alerts.csv", "results/recommendations.csv", "results/coverage_gaps.csv",
        "results/sql_parity.csv", "model/DATA_MODEL.md", "model/DAX_MEASURES.md",
        "powerbi/PAGE_PLAN.md", "powerbi/POWER_QUERY.md", "powerbi/EXPORT_PREVIEWS.md",
        "qa/CHECKLIST.md", "qa/INTERACTION_TESTS.md",
    ]
    missing_files = [name for name in required if not (ROOT / name).is_file()]

    summary_block = "\n".join([
        f"- **Période et source :** sept exercices 2019–2025, quinze indicateurs et 105 valeurs extraites des 10-K annuels de la SEC.",
        f"- **Dernier exercice :** produits {fr_num(latest['revenue']/1e9, 2)} Md USD, résultat net {fr_num(latest['net_income']/1e9, 2)} Md USD, marge opérationnelle {fr_pct(latest['operating_margin'], 2)}, ROE {fr_pct(latest['roe'], 2)}.",
        f"- **Structure et trésorerie :** liquidité courante {fr_ratio(latest['current_ratio'], 2)}, passif/actif {fr_pct(latest['debt_ratio'], 2)}, flux disponible {fr_num(latest['fcf']/1e9, 2)} Md USD ({fr_pct(latest['fcf_margin'], 2)} des produits).",
        f"- **Livrables automatisés :** {table_count} tables Power BI, {dax_count} mesures DAX, {page_count} pages planifiées, {visual_count} graphiques, {sql_passes}/{len(parity)} comparaisons SQL/Python; dashboard manuel à construire.",
    ])
    key_results = "\n".join([
        "| Indicateur | Résultat | Référence |",
        "|---|---|---|",
        f"| Produits {latest_year} | {fr_num(latest['revenue']/1e9, 2)} Md USD; croissance {fr_pct(latest['revenue_growth'], 2)} | `results/annual_kpis.csv` |",
        f"| Marge opérationnelle | {fr_pct(latest['operating_margin'], 2)} en {latest_year} contre {fr_pct(annual.loc[prior_year, 'operating_margin'], 2)} en {prior_year} | `results/ratio_summary.csv` |",
        f"| ROE et ROA | {fr_pct(latest['roe'], 2)} et {fr_pct(latest['roa'], 2)} | `results/annual_kpis.csv` |",
        f"| Liquidité et dette | liquidité {fr_ratio(latest['current_ratio'], 2)}; passif/actif {fr_pct(latest['debt_ratio'], 2)}; couverture {fr_ratio(latest['interest_coverage'], 1)}x | `results/annual_kpis.csv` |",
        f"| Flux disponible | {fr_num(latest['fcf']/1e9, 2)} Md USD, soit {fr_pct(latest['fcf_margin'], 2)} des produits | `results/annual_kpis.csv` |",
        f"| Parité SQL/Python | {sql_passes}/{len(parity)} PASS | `results/sql_parity.csv` |",
    ])
    recommendation_md = "\n".join([
        "| Priorité | Recommandation | Évidence calculée |",
        "|---:|---|---|",
        *[f"| {int(row.priority)} | {str(row.recommendation).replace('|', '/')} | {str(row.evidence).replace('|', '/')} |" for row in recommendations.itertuples(index=False)],
    ])
    dax_expected = render_dax_expected(latest)
    dax_text = replace_block(dax_text, "<!-- AUTO:DAX_EXPECTED_BEGIN -->", "<!-- AUTO:DAX_EXPECTED_END -->", dax_expected)
    dax_path.write_text(dax_text, encoding="utf-8")

    project_status_placeholder = "EN COURS"
    readme_text = replace_block(readme_text, "<!-- AUTO:SUMMARY_BEGIN -->", "<!-- AUTO:SUMMARY_END -->", summary_block)
    readme_text = replace_block(readme_text, "<!-- AUTO:KEY_RESULTS_BEGIN -->", "<!-- AUTO:KEY_RESULTS_END -->", key_results)
    readme_text = replace_block(readme_text, "<!-- AUTO:RECOMMENDATIONS_BEGIN -->", "<!-- AUTO:RECOMMENDATIONS_END -->", recommendation_md)
    qa_status = f"**Automatisé :** `{project_status_placeholder}` selon [`qa/validation_report.md`](qa/validation_report.md). **Manuel Power BI :** à faire par Samuel; aucune validation Desktop n’est revendiquée."
    readme_text = replace_block(readme_text, "<!-- AUTO:QA_STATUS_BEGIN -->", "<!-- AUTO:QA_STATUS_END -->", qa_status)
    readme_path.write_text(readme_text, encoding="utf-8")

    root_readme_path = REPO / "README.md"
    root_readme = root_readme_path.read_text(encoding="utf-8")
    root_row = (
        f"| 06 | [Analyse financière de Mastercard](projects/06-analyse-financiere/README.md) | "
        f"Protéger la marge; marge opérationnelle **{fr_pct(latest['operating_margin'], 2)}**. | "
        f"Python · pandas · SQLite · Power BI/DAX | Analyse terminée; dashboard à construire par Samuel |"
    )
    row_pattern = re.compile(r"(?m)^\| 06 \| \[Analyse financi.*$")
    root_readme, row_count = row_pattern.subn(root_row, root_readme, count=1)
    if row_count != 1:
        raise SystemExit("Ligne projet 06 absente du README racine; ajouter la ligne d'index avant run_all.py.")
    root_status = "\n".join([
        "| Données | Qualité | SQL/Python | DAX | Rapport QA | Dashboard Power BI |",
        "|---|---|---|---|---|---|",
        f"| 7 exercices · 105 valeurs | {project_status_placeholder} | {sql_passes}/{len(parity)} comparaisons | {dax_count} mesures | {project_status_placeholder} | À construire par Samuel |",
    ])
    root_readme = replace_block(root_readme, "<!-- AUTO:PROJECT06_STATUS_BEGIN -->", "<!-- AUTO:PROJECT06_STATUS_END -->", root_status)
    root_readme_path.write_text(root_readme, encoding="utf-8")

    (ROOT / "qa/validation_report.md").write_text(
        "# Rapport de validation automatique — projet 06\n\nGénération en cours par `scripts/05_report.py`.\n",
        encoding="utf-8")

    docs_to_check = [*ROOT.rglob("*.md"), root_readme_path, REPO / "docs/ROADMAP.md"]
    link_errors = broken_links(docs_to_check)
    line_count = len(readme_path.read_text(encoding="utf-8").splitlines())
    text_extensions = {".md", ".py", ".sql", ".txt", ".csv"}
    self_referential = {ROOT / "scripts/05_report.py", ROOT / "qa/validation_report.md"}
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
    record("Empreinte de la source", "SHA-256 et taille conformes", "conforme" if raw_ok else "écart détecté", raw_ok)
    record("Contrôles qualité", "Aucun FAIL", f"{quality_failures} FAIL; {len(quality)} règles", quality_failures == 0)
    fact_ratios_frame = pd.read_csv(processed / "fact_ratios.csv")
    fact_financials_frame = pd.read_csv(processed / "fact_financials.csv")
    completeness_ok = len(fact_ratios_frame) == 130 and len(fact_financials_frame) == 105
    record("Complétude", "105 valeurs comptables; 130 ratios", f"{len(fact_financials_frame)} valeurs; {len(fact_ratios_frame)} ratios", completeness_ok)
    record("Parité SQL/Python", "Au moins 5 requêtes, tous PASS", f"{sql_queries} requêtes; {sql_passes}/{len(parity)} PASS; {sql_failures} FAIL", sql_queries >= 5 and sql_failures == 0 and sql_passes == len(parity))
    record("Tables Power BI", "7 CSV traités", f"{table_count}/7 présents", table_count == 7)
    record("Mesures DAX", "Définitions numérotées et valeurs générées", f"{dax_count} mesures", dax_count == 15)
    record("Pages planifiées", "4 pages", f"{page_count} pages", page_count == 4)
    record("Graphiques", "Au moins 6 PNG Matplotlib", f"{visual_count} PNG", visual_count >= 6)
    record("README projet", "Au plus 120 lignes; badge PORTFOLIO", f"{line_count} lignes; badge {'présent' if markdown_badge else 'absent'}", line_count <= 120 and markdown_badge)
    record("Liens relatifs/images", "Tous résolus", f"{len(link_errors)} cassé(s)", len(link_errors) == 0)
    record("Taille du projet", "<25 Mo; aucun fichier >50 Mo", f"{total_bytes/1_000_000:.2f} Mo; maximum {largest_bytes/1_000_000:.2f} Mo", total_bytes < MAX_PROJECT_BYTES and not over_50mb)
    record("Caches Python", "Aucun", f"{len(caches)} artefact(s)", len(caches) == 0)
    record("Conformité texte", "Aucun chemin absolu, TODO, LinkedIn ou emoji", f"{len(absolute_paths)} chemin(s), {todos} TODO, {linked_in} LinkedIn, {emoji} emoji", not absolute_paths and todos == 0 and linked_in == 0 and emoji == 0)
    record("Dépendances", "Versions directes épinglées avec ==", f"{len(requirements)} dépendances", pinned)
    record("Formats interdits", "Aucun HTML/Excel/PBIX/PBIP/PBIR/TMDL", f"{len(forbidden)} fichier(s)", not forbidden)
    record("Checklist Desktop", "Tous les tests manuels restent non cochés", f"{len(manual_marks)} cases; toutes non cochées={manual_all_unchecked}", manual_all_unchecked)

    overall_status = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    readme_text = readme_path.read_text(encoding="utf-8")
    qa_status = f"**Automatisé :** `{overall_status}` selon [`qa/validation_report.md`](qa/validation_report.md). **Manuel Power BI :** à faire par Samuel; aucune validation Desktop n’est revendiquée."
    readme_text = replace_block(readme_text, "<!-- AUTO:QA_STATUS_BEGIN -->", "<!-- AUTO:QA_STATUS_END -->", qa_status)
    readme_path.write_text(readme_text, encoding="utf-8")

    root_readme = root_readme_path.read_text(encoding="utf-8")
    root_status = "\n".join([
        "| Données | Qualité | SQL/Python | DAX | Rapport QA | Dashboard Power BI |",
        "|---|---|---|---|---|---|",
        f"| 7 exercices · 105 valeurs | {overall_status} | {sql_passes}/{len(parity)} comparaisons | {dax_count} mesures | {overall_status} | À construire par Samuel |",
    ])
    root_readme = replace_block(root_readme, "<!-- AUTO:PROJECT06_STATUS_BEGIN -->", "<!-- AUTO:PROJECT06_STATUS_END -->", root_status)
    root_readme_path.write_text(root_readme, encoding="utf-8")

    report = [
        "# Rapport de validation automatique — projet 06",
        "",
        f"**Statut automatisé : {overall_status}.** Généré par `scripts/05_report.py` depuis les sorties du pipeline. Les tests Desktop sont séparés et restent à faire par Samuel.",
        "",
        "| Contrôle | Attendu | Constaté | Statut |",
        "|---|---|---|---|",
        *[f"| {item['label']} | {item['expected']} | {item['observed']} | {item['status']} |" for item in checks],
        "",
        f"**Source :** SEC EDGAR companyfacts, CIK 1141391; SHA-256 `{RAW_SHA256}`; {RAW_BYTES:,} octets; exercices 2019–2025.",
        f"**Dernier exercice :** produits {fr_num(latest['revenue'])} USD; résultat net {fr_num(latest['net_income'])} USD; marge opérationnelle {fr_pct(latest['operating_margin'], 3)}; ROE {fr_pct(latest['roe'], 3)}; liquidité {fr_ratio(latest['current_ratio'], 3)}; flux disponible {fr_num(latest['fcf'])} USD.",
        f"**Ratios :** {len(summary)} ratios calculés, dont la croissance des produits à {fr_pct(growth.loc['revenue', 'cagr'], 3)} en moyenne annuelle sur la période; aucune valeur n’est extrapolée hors des sept exercices.",
        "**Manuel :** le dashboard Power BI, les mesures saisies dans Desktop, les scénarios d’interaction et les exports PDF/PNG ne sont pas exécutés dans cette livraison.",
    ]
    (ROOT / "qa/validation_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    final_link_errors = broken_links([*ROOT.rglob("*.md"), root_readme_path, REPO / "docs/ROADMAP.md"])
    if final_link_errors:
        raise SystemExit("Lien(s) cassé(s) après génération: " + "; ".join(final_link_errors))
    print(f"Rapport QA {overall_status}: {len(checks)} contrôles; {sql_passes}/{len(parity)} parités SQL; {table_count} tables, {dax_count} mesures, {page_count} pages planifiées.")
    if overall_status != "PASS":
        raise SystemExit("Au moins un contrôle QA est en échec; consulter qa/validation_report.md.")


if __name__ == "__main__":
    main()
