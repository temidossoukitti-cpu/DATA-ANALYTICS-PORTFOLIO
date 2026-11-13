"""Génère dashboard/web/data.js à partir des tables traitées et des résultats (aucune valeur inventée)."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P, R = ROOT / "data/processed", ROOT / "results"

bands = pd.read_csv(P / "dim_amount_band.csv").sort_values("sort_order")
wins = pd.read_csv(P / "dim_time_window.csv").sort_values("sort_order")
bi = {k: i for i, k in enumerate(bands["amount_band_key"])}
wi = {k: i for i, k in enumerate(wins["time_window_key"])}

f = pd.read_csv(P / "fact_transactions.csv")
f["aw"] = f["amount"] * f["sampling_weight"]
g = f.groupby(["amount_band_key", "time_window_key", "outcome_key"]).agg(nw=("sampling_weight", "sum"), aw=("aw", "sum")).reset_index()
cube = [[bi[r.amount_band_key], wi[r.time_window_key], int(r.outcome_key), round(r.nw, 3), round(r.aw, 2)] for r in g.itertuples()]

t = pd.read_csv(P / "fact_model_test.csv")
T = {"p": t["model_probability"].round(8).tolist(), "a": t["amount"].round(2).tolist(),
     "y": t["outcome_key"].astype(int).tolist(), "w": t["eval_population_weight"].round(6).tolist(),
     "r": t["baseline_amount_flag"].astype(int).tolist(), "b": [bi[int(k)] for k in t["amount_band_key"]]}

# contrôle : coût au seuil 0,191 avec frais de 10 et sévérité 1,0 vs results/model_metrics et money_controls
fl = t["model_probability"] >= 0.191
cost = (t.loc[fl & (t.outcome_key == 0), "eval_population_weight"].sum() * 10
        + (t.loc[~fl & (t.outcome_key == 1), "eval_population_weight"] * t.loc[~fl & (t.outcome_key == 1), "amount"]).sum())
ref = pd.read_csv(R / "model_scorecard.csv")["expected_cost_test"].iloc[0]
print("coût recalculé:", round(cost, 1), "| coût du dépôt:", round(ref, 1))

k = pd.read_csv(R / "overall_kpis.csv").set_index("metric")["value"]
pop = {"n": float(k["transactions_population_exact"]), "f": float(k["fraud_transactions_population_exact"]),
       "a": float(k["amount_total_population_exact"]), "fa": float(k["fraud_amount_population_exact"])}
gaps = pd.read_csv(R / "coverage_gaps.csv")[["field", "handling"]].values.tolist()

data = {"bands": bands["label_fr"].tolist(), "wins": wins["label_fr"].tolist(), "cube": cube, "test": T,
        "pop": pop, "gaps": gaps, "sample_rows": int(len(f)), "th0": 0.191, "fr0": 10, "sv0": 1.0}
out = ROOT / "dashboard/web/data.js"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("window.DATA=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
print("OK ->", out, round(out.stat().st_size / 1024), "Ko")
