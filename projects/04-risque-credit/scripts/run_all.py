"""Point d’entrée unique; exécute toutes les étapes dans l’ordre depuis un clone propre."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_NAMES = [
    "01_clean.py",
    "02_analyze.py",
    "03_model.py",
    "04_scorecard.py",
    "05_sql.py",
    "06_report.py",
]


def main() -> None:
    if sys.version_info < (3, 11):
        raise SystemExit("Python 3.11 ou plus récent est requis.")
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["MPLBACKEND"] = "Agg"
    for script_name in SCRIPT_NAMES:
        script_path = PROJECT_ROOT / "scripts" / script_name
        print(f"\n=== {script_name} ===", flush=True)
        subprocess.run(
            [sys.executable, str(script_path)],
            cwd=PROJECT_ROOT,
            check=True,
            env=environment,
        )
    print("\nPipeline terminé sans étape manuelle ni accès réseau.", flush=True)


if __name__ == "__main__":
    main()
