from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dashboard" / "web" / "data.js"

annual = pd.read_csv(ROOT / "results" / "annual_kpis.csv")
ratios = pd.read_csv(ROOT / "results" / "ratio_summary.csv")
alerts = pd.read_csv(ROOT / "results" / "alerts.csv")
growth = pd.read_csv(ROOT / "results" / "growth_summary.csv")
gaps = pd.read_csv(ROOT / "results" / "coverage_gaps.csv")
recs = pd.read_csv(ROOT / "results" / "recommendations.csv")

def records(df):
    return json.loads(df.to_json(orient="records"))

payload = {
    "entity": "Mastercard Incorporated",
    "annual": records(annual),
    "ratios": records(ratios),
    "alerts": records(alerts),
    "growth": records(growth),
    "gaps": records(gaps),
    "recommendations": records(recs),
    "meta": {"source": "SEC EDGAR companyfacts · CIK 1141391", "period": "2019–2025", "qa": "109/109 comparaisons SQL/Python"},
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("const DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
print(f"{OUT}: {len(annual)} annual rows, {len(ratios)} ratios")
