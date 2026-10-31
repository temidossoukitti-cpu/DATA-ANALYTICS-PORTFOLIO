"""Projet 1 - Analyse de risque et de performance d'un portefeuille d'actions.
Usage : python scripts/analysis.py   (depuis le dossier du projet)
Entrees : data/raw/*.csv    Sorties : data/cleaned/ et results/
"""
import numpy as np, pandas as pd
from scipy.optimize import minimize

RF, ANN = 0.035, 52          # taux sans risque annuel, periodes par an (hebdo)
raw, clean, out = "data/raw/", "data/cleaned/", "results/"

# 1. Chargement et controle qualite -------------------------------------------
px = pd.read_csv(raw + "prices_weekly.csv", parse_dates=["date"]).set_index("date").sort_index()
assets = pd.read_csv(raw + "assets.csv"); hold = pd.read_csv(raw + "holdings.csv")
qc = {"lignes": len(px), "colonnes": px.shape[1], "doublons_dates": int(px.index.duplicated().sum()),
      "valeurs_manquantes": int(px.isna().sum().sum()), "prix_negatifs_ou_nuls": int((px <= 0).sum().sum()),
      "date_debut": str(px.index.min().date()), "date_fin": str(px.index.max().date())}
px.to_csv(clean + "prices_weekly_clean.csv")
pd.Series(qc).to_csv(out + "quality_check.csv", header=["valeur"])

# 2. Rendements et poids ------------------------------------------------------
r = px.pct_change().dropna(); tick = list(hold.ticker)
mv = hold.set_index("ticker").shares * px.iloc[-1][tick]; w = mv / mv.sum()
pd.DataFrame({"ticker": w.index, "valeur_marche": mv.values.round(0), "poids": w.values.round(4)}
             ).merge(assets[["ticker", "sector"]], on="ticker").to_csv(out + "weights.csv", index=False)

# 3. Indicateurs de portefeuille ---------------------------------------------
def stats(rp, rm):
    mu = (1 + rp).prod() ** (ANN / len(rp)) - 1; vol = rp.std() * np.sqrt(ANN)
    cum = (1 + rp).cumprod(); mdd = (cum / cum.cummax() - 1).min()
    mu_m = (1 + rm).prod() ** (ANN / len(rm)) - 1
    beta = np.cov(rp, rm)[0, 1] / rm.var(); alpha = (mu - RF) - beta * (mu_m - RF)
    return {"rendement_annualise": mu, "volatilite_annualisee": vol, "ratio_sharpe": (mu - RF) / vol,
            "drawdown_max": mdd, "beta_vs_IDX": beta, "alpha_annualise": alpha,
            "VaR_95_hebdo": -np.percentile(rp, 5), "pire_semaine": rp.min(), "meilleure_semaine": rp.max()}
rm = r["IDX"]; rp = (r[tick] * w).sum(axis=1)
m = pd.DataFrame({"portefeuille": stats(rp, rm), "indice_IDX": stats(rm, rm)}).T
m.round(4).to_csv(out + "metrics_portfolio_vs_index.csv")

# 4. Indicateurs par actif et correlations ------------------------------------
rows = []
for t in tick:
    s = stats(r[t], rm); rows.append({"ticker": t, **{k: round(s[k], 4) for k in ["rendement_annualise", "volatilite_annualisee", "ratio_sharpe", "drawdown_max", "beta_vs_IDX"]}})
pd.DataFrame(rows).merge(assets[["ticker", "sector"]], on="ticker").to_csv(out + "metrics_by_asset.csv", index=False)
r[tick].corr().round(3).to_csv(out + "correlation_matrix.csv")

# 5. Contribution au risque ---------------------------------------------------
cov = r[tick].cov() * ANN; wv = w.values; pv = float(np.sqrt(wv @ cov.values @ wv))
rc = wv * (cov.values @ wv) / pv
pd.DataFrame({"ticker": tick, "poids": wv.round(4), "contribution_risque": (rc / pv).round(4)}).to_csv(out + "risk_contribution.csv", index=False)

# 6. Optimisation : variance minimale et frontiere efficiente (long only) -----
mu_a = ((1 + r[tick]).prod() ** (ANN / len(r)) - 1).values; n = len(tick)
cons0 = [{"type": "eq", "fun": lambda x: x.sum() - 1}]; bnds = [(0, 0.35)] * n
def vol_f(x): return float(np.sqrt(x @ cov.values @ x))
mv_w = minimize(vol_f, np.ones(n) / n, bounds=bnds, constraints=cons0).x
sh_w = minimize(lambda x: -((x @ mu_a - RF) / vol_f(x)), np.ones(n) / n, bounds=bnds, constraints=cons0).x
def pf(x): return {"rendement": round(float(x @ mu_a), 4), "volatilite": round(vol_f(x), 4), "sharpe": round(float((x @ mu_a - RF) / vol_f(x)), 3)}
pd.DataFrame({"actuel": pf(wv), "variance_minimale": pf(mv_w), "sharpe_maximal": pf(sh_w)}).T.to_csv(out + "optimization_summary.csv")
pd.DataFrame({"ticker": tick, "actuel": wv.round(4), "variance_minimale": mv_w.round(4), "sharpe_maximal": sh_w.round(4)}).to_csv(out + "optimization_weights.csv", index=False)
fr = []
for target in np.linspace(mu_a.min() + .005, mu_a.max() - .005, 25):
    c = cons0 + [{"type": "eq", "fun": lambda x, t=target: x @ mu_a - t}]
    s = minimize(vol_f, np.ones(n) / n, bounds=bnds, constraints=c)
    if s.success: fr.append({"rendement": round(target, 4), "volatilite": round(vol_f(s.x), 4)})
pd.DataFrame(fr).to_csv(out + "efficient_frontier.csv", index=False)

# 7. Serie de valeur du portefeuille (base 100) -------------------------------
pd.DataFrame({"portefeuille": 100 * (1 + rp).cumprod(), "IDX": 100 * (1 + rm).cumprod()}).round(2).to_csv(out + "performance_base100.csv")
print("OK - resultats ecrits dans results/")

# 8. Tables prêtes pour Power BI ------------------------------------------------
rp.rename("portefeuille").to_frame().join(rm.rename("IDX")).round(6).to_csv(out + "portfolio_returns.csv")
long = px.reset_index().melt(id_vars="date", var_name="ticker", value_name="close").sort_values(["ticker", "date"])
long["rendement"] = long.groupby("ticker")["close"].pct_change().round(6)
long.to_csv(clean + "prices_long.csv", index=False)
