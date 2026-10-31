"""Exécute le pipeline reproductible depuis l'échantillon versionné."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
STAGES = [
    "01_clean.py",
    "02_analyze.py",
    "03_model.py",
    "04_scorecard.py",
    "05_sql.py",
    "06_report.py",
]


def main() -> None:
    sample = ROOT / "data/processed/transactions_sample.parquet"
    population = ROOT / "results/population_kpis.csv"
    if not sample.is_file() or not population.is_file():
        raise SystemExit("Échantillon/KPI source absents. Recréer d'abord avec scripts/00_make_sample.py et le Parquet officiel documenté dans data/raw/SOURCE.md.")
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["MPLBACKEND"] = "Agg"
    for stage in STAGES:
        script = ROOT / "scripts" / stage
        print(f"\n=== {stage} ===", flush=True)
        subprocess.run([sys.executable, str(script)], cwd=ROOT, env=env, check=True)
    caches = [path for path in ROOT.rglob("__pycache__") if path.is_dir()]
    bytecode = list(ROOT.rglob("*.pyc"))
    if caches or bytecode:
        raise SystemExit(f"Caches Python détectés : {len(caches)} dossier(s), {len(bytecode)} fichier(s).")
    print("\nPipeline complet : PASS. Le dashboard Power BI reste à construire manuellement par Samuel.")


if __name__ == "__main__":
    main()
