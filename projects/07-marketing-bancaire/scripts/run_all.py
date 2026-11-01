"""Exécute le pipeline complet du projet 07 dans l'ordre déterministe."""
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).parent
for script in ("01_clean.py", "02_analyze.py", "03_model.py"):
    print(f"\n=== {script} ===")
    runpy.run_path(str(ROOT / script), run_name="__main__")

print("\nPipeline terminé : données nettoyées, analyses, graphiques et métriques générés.")
