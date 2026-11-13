"""Agrège data/processed/fact_clients.csv en un cube compact : dashboard/web/data.js."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data/processed"
f = pd.read_csv(P / "fact_clients.csv")
lab = lambda d, k, l: dict(zip(pd.read_csv(P / d)[k], pd.read_csv(P / d)[l]))

f["limite"] = f["limit_band"]
f["age_b"] = f["age_band"]
f["edu"] = f["education_key"].map(lab("dim_education.csv", "education_key", "education_label"))
f["mar"] = f["marriage_key"].map(lab("dim_marriage.csv", "marriage_key", "marriage_label"))
f["risk"] = f["risk_band_key"].map(lab("dim_risk_band.csv", "risk_band_key", "risk_band_label"))
f["pay"] = pd.cut(f["pay_0"], [-9, -1, 0, 1, 2, 99],
                  labels=["À jour / sans achat", "Crédit renouvelable", "Retard 1 mois", "Retard 2 mois", "Retard 3 mois et +"]).astype(str)

dims = ["limite", "age_b", "edu", "mar", "risk", "pay"]
order = {
    "limite": ["Q1", "Q2", "Q3", "Q4", "Q5"],
    "age_b": ["<25", "25-34", "35-44", "45-54", "55+"],
    "edu": list(pd.read_csv(P / "dim_education.csv")["education_label"]),
    "mar": list(pd.read_csv(P / "dim_marriage.csv")["marriage_label"]),
    "risk": list(pd.read_csv(P / "dim_risk_band.csv")["risk_band_label"]),
    "pay": ["À jour / sans achat", "Crédit renouvelable", "Retard 1 mois", "Retard 2 mois", "Retard 3 mois et +"],
}
f["n"], f["d"] = 1, f["default_next_month"]
f["lim"], f["dlim"] = f["limit_bal"], f["limit_bal"] * f["default_next_month"]
f["u"] = f["utilization"]
late = ["pay_6", "pay_5", "pay_4", "pay_3", "pay_2", "pay_0"]          # avril -> septembre 2005
bill = ["bill_amt6", "bill_amt5", "bill_amt4", "bill_amt3", "bill_amt2", "bill_amt1"]
for i, c in enumerate(late): f[f"l{i}"] = (f[c] > 0).astype(int)
for i, c in enumerate(bill): f[f"b{i}"] = f[c]
vals = ["n", "d", "lim", "dlim", "u"] + [f"l{i}" for i in range(6)] + [f"b{i}" for i in range(6)]

g = f.groupby(dims, observed=True)[vals].sum().reset_index()
for d in dims: g[d] = g[d].map({v: i for i, v in enumerate(order[d])})
g = g.dropna()
rows = [[int(x) for x in r[:6]] + [round(float(x), 2) for x in r[6:]] for r in g.to_numpy()]

out = ROOT / "dashboard/web/data.js"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("window.DATA=" + json.dumps({"dims": dims, "labels": order, "rows": rows}, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
print("OK", len(rows), "cellules ->", out)
