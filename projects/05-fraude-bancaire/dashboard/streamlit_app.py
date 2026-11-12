from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "processed"
RESULTS_DIR = PROJECT_DIR / "results"
BLACK, CARD, RED, GREY, MUTED, WHITE = "#050505", "#141414", "#d92b2b", "#2a2a2e", "#8a8a90", "#ffffff"

st.set_page_config(page_title="Fraud Monitor · Projet 05", page_icon="●", layout="wide", initial_sidebar_state="expanded")
st.markdown(f"""
<style>
.stApp {{ background:#e8e8ec; color:#161616; }}
[data-testid="stSidebar"] {{ background:{BLACK}; }}
[data-testid="stSidebar"] * {{ color:{WHITE} !important; }}
.block-container {{ max-width:1440px; padding-top:1rem; }}
.hero {{ background:{BLACK}; color:{WHITE}; padding:20px 26px 22px; border-radius:0 0 22px 22px; margin:-1rem -1rem 1rem; }}
.hero h1 {{ margin:0; font-size:1.55rem; }}
.hero p {{ color:#c9c9cf; margin:.2rem 0 0; }}
.kpi {{ background:{CARD}; color:{WHITE}; border:1px solid #3a3a3a; border-radius:14px; padding:12px 16px; min-height:82px; }}
.kpi small {{ color:#c9c9cf; display:block; font-size:.72rem; }}
.kpi b {{ display:block; font-size:1.4rem; margin-top:.35rem; }}
.card {{ background:#fff; border-radius:12px; padding:14px 16px; box-shadow:0 2px 7px #0002; }}
.note {{ color:{MUTED}; font-size:.75rem; }}
[data-testid="stMetric"] {{ background:{CARD}; border:1px solid #3a3a3a; border-radius:12px; padding:10px 14px; }}
[data-testid="stMetric"] label, [data-testid="stMetricValue"] {{ color:{WHITE} !important; }}
[data-testid="stMetricDelta"] {{ color:#f07a7a !important; }}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_tables():
    tx = pd.read_csv(DATA_DIR / "fact_transactions.csv")
    test = pd.read_csv(DATA_DIR / "fact_model_test.csv")
    bands = pd.read_csv(DATA_DIR / "dim_amount_band.csv").sort_values("sort_order")
    wins = pd.read_csv(DATA_DIR / "dim_time_window.csv").sort_values("sort_order")
    overall = pd.read_csv(RESULTS_DIR / "overall_kpis.csv")
    metrics = pd.read_csv(RESULTS_DIR / "model_metrics.csv")
    scorecard = pd.read_csv(RESULTS_DIR / "model_scorecard.csv")
    gaps = pd.read_csv(RESULTS_DIR / "coverage_gaps.csv")
    return tx, test, bands, wins, overall, metrics, scorecard, gaps

# Keep the same weighted aggregation and scenario formulas as dashboard/web/index.html.
tx, test, bands, wins, overall, metrics, scorecard, gaps = load_tables()

def kpi(metric: str) -> float:
    return float(overall.loc[overall.metric == metric, "value"].iloc[0])

def agg_transactions(band_key=None, win_key=None):
    x = tx.copy()
    if band_key is not None: x = x[x.amount_band_key == band_key]
    if win_key is not None: x = x[x.time_window_key == win_key]
    n = float(x.sampling_weight.sum())
    f = float(x.loc[x.outcome_key == 1, "sampling_weight"].sum())
    amount = float((x.amount * x.sampling_weight).sum())
    fraud_amount = float((x.loc[x.outcome_key == 1, "amount"] * x.loc[x.outcome_key == 1, "sampling_weight"]).sum())
    return {"n": n, "f": f, "a": amount, "fa": fraud_amount}

def simulate(threshold: float, friction: float, severity: float, amount_rule: bool = False):
    flagged = test.baseline_amount_flag.eq(1) if amount_rule else test.model_probability.ge(threshold)
    tp = float(test.loc[flagged & test.outcome_key.eq(1), "eval_population_weight"].sum())
    fp = float(test.loc[flagged & test.outcome_key.eq(0), "eval_population_weight"].sum())
    fn = float(test.loc[~flagged & test.outcome_key.eq(1), "eval_population_weight"].sum())
    missed_amount = float((test.loc[~flagged & test.outcome_key.eq(1), "eval_population_weight"] * test.loc[~flagged & test.outcome_key.eq(1), "amount"]).sum())
    cost = fp * friction + missed_amount * severity
    return {"alerts": tp + fp, "tp": tp, "fp": fp, "fn": fn, "precision": tp / (tp + fp or 1), "recall": tp / (tp + fn or 1), "cost": cost, "missed": missed_amount}

def fmt_num(x, d=0): return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
def pct(x, d=2): return f"{100*x:.{d}f}%".replace(".", ",")

def style(fig, height=330):
    fig.update_layout(height=height, margin=dict(l=20,r=20,t=28,b=20), paper_bgcolor="white", plot_bgcolor="white", font=dict(color="#161616"), showlegend=False)
    fig.update_xaxes(showgrid=False, linecolor="#e1e1e6")
    fig.update_yaxes(gridcolor="#eeeeF2", zerolinecolor="#e1e1e6")
    return fig

with st.sidebar:
    st.markdown("## Fraud Monitor")
    st.caption("DÉTECTION DE FRAUDE · PROJET 05")
    st.divider()
    page = st.radio("Navigation", ["Vue d'ensemble", "Scénario", "Segmentation et limites"], label_visibility="collapsed")
    st.divider()
    st.caption("Source : OpenML dataset 43627")
    st.caption("Montants en unités du dataset · coûts hypothétiques")

population = kpi("transactions_population_exact")
frauds = kpi("fraud_transactions_population_exact")
rate = kpi("fraud_rate_population_exact")
amount_total = kpi("amount_total_population_exact")
amount_fraud = kpi("fraud_amount_population_exact")

st.markdown(f'<div class="hero"><h1>Fraud Monitor</h1><p>{page} · Prioriser la revue sans confondre score de risque et blocage automatique</p></div>', unsafe_allow_html=True)
cols = st.columns(5)
for col, label, value in zip(cols, ["Transactions", "Fraudes", "Taux de fraude", "Montant total", "Montant frauduleux"], [fmt_num(population), fmt_num(frauds), pct(rate, 3), fmt_num(amount_total/1e6,2)+" M", fmt_num(amount_fraud)]):
    col.markdown(f'<div class="kpi"><small>{label}</small><b>{value}</b></div>', unsafe_allow_html=True)
st.write("")

if page == "Vue d'ensemble":
    c1, c2 = st.columns([1.35, 1])
    with c1:
        st.subheader("Taux de fraude par fenêtre de 6 h")
        win_rows = []
        for _, w in wins.iterrows():
            a = agg_transactions(win_key=int(w.time_window_key)); win_rows.append({"Fenêtre": w.label_fr, "Taux": a["f"] / a["n"] if a["n"] else 0})
        wf = pd.DataFrame(win_rows)
        fig = px.bar(wf, x="Fenêtre", y="Taux", color="Taux", color_continuous_scale=[(0,"#2a2a2e"),(1,RED)])
        fig.update_yaxes(tickformat=".2%", title="Taux pondéré"); st.plotly_chart(style(fig), width="stretch")
    with c2:
        st.subheader("Montant frauduleux par tranche")
        band_rows=[]
        for _, b in bands.iterrows():
            a=agg_transactions(band_key=int(b.amount_band_key)); band_rows.append({"Tranche":b.label_fr,"Montant frauduleux":a["fa"]})
        bf=pd.DataFrame(band_rows); fig=px.pie(bf,names="Tranche",values="Montant frauduleux",hole=.62,color_discrete_sequence=[RED,BLACK,"#7d7d84","#c9c9cf"]); fig.update_traces(textinfo="percent", hovertemplate="%{label}<br>%{value:,.0f}<extra></extra>"); st.plotly_chart(style(fig,300),width="stretch")
    c3, c4 = st.columns([1.35,1])
    with c3:
        st.subheader("Taux de fraude par tranche de montant")
        rows=[]
        for _,b in bands.iterrows():
            a=agg_transactions(band_key=int(b.amount_band_key)); rows.append({"Tranche":b.label_fr,"Taux":a["f"]/a["n"] if a["n"] else 0})
        fig=px.bar(pd.DataFrame(rows),x="Tranche",y="Taux",color="Taux",color_continuous_scale=[(0,"#8a8a90"),(1,RED)]); fig.update_yaxes(tickformat=".2%",title="Taux pondéré"); st.plotly_chart(style(fig),width="stretch")
    with c4:
        st.subheader("Fenêtres les plus exposées")
        top=wf.sort_values("Taux",ascending=False).head(5).copy(); top["Taux"]=top["Taux"].map(lambda x:pct(x,3)); st.dataframe(top,hide_index=True,width="stretch")

elif page == "Scénario":
    st.subheader("Analyse de scénario")
    st.caption("Référence : seuil 0,191, friction 10 et sévérité 100 %. Les coûts sont des hypothèses.")
    threshold=st.slider("Seuil de décision du modèle",0.01,0.99,0.191,0.005)
    friction=st.slider("Coût de friction par alerte légitime",0,50,10,1)
    severity=st.slider("Sévérité de perte sur fraude manquée",0.5,1.5,1.0,0.1)
    ref=simulate(0.191,10,1.0); sim=simulate(threshold,friction,severity); rule=simulate(0,10,1.0,True)
    a,b,c,d,e=st.columns(5)
    for col,label,val in zip([a,b,c,d,e],["Alertes","Coût estimé","Précision","Rappel","Fraude manquée"],[sim["alerts"],sim["cost"],sim["precision"],sim["recall"],sim["missed"]]): col.metric(label,fmt_num(val,0) if label not in ("Précision","Rappel") else pct(val,1))
    st.write("")
    left,right=st.columns([1.2,1])
    with left:
        curve=pd.read_csv(RESULTS_DIR/"threshold_curve.csv"); fig=px.line(curve,x="threshold",y="expected_cost_train_oof",labels={"threshold":"Seuil","expected_cost_train_oof":"Coût estimé"}); fig.add_vline(x=0.191,line_dash="dash",line_color=GREY); fig.add_vline(x=threshold,line_color=RED); st.plotly_chart(style(fig),width="stretch")
    with right:
        comp=pd.DataFrame({"Indicateur":["Alertes","Coût","Précision","Rappel"],"Référence":[ref["alerts"],ref["cost"],ref["precision"],ref["recall"]],"Simulation":[sim["alerts"],sim["cost"],sim["precision"],sim["recall"]]}); st.dataframe(comp,hide_index=True,width="stretch")
        st.info(f"Règle montant P99 : {fmt_num(rule['alerts'])} alertes, rappel {pct(rule['recall'],1)}, coût {fmt_num(rule['cost'])} unités.")

else:
    st.subheader("Segmentation et limites des données")
    st.caption("Taux pondéré par fenêtre relative et tranche de montant")
    matrix=[]
    for _,w in wins.iterrows():
        row={"Fenêtre":w.label_fr}
        for _,b in bands.iterrows():
            a=agg_transactions(int(b.amount_band_key),int(w.time_window_key)); row[b.label_fr]=a["f"]/a["n"] if a["n"] else 0
        matrix.append(row)
    md=pd.DataFrame(matrix).set_index("Fenêtre"); st.dataframe(md.style.format(lambda x:pct(x,3)).background_gradient(cmap="Reds"),width="stretch")
    st.subheader("Limites documentées")
    st.dataframe(gaps.rename(columns={"field":"Information absente","handling":"Traitement"}),hide_index=True,width="stretch")

st.markdown('<div class="note">Source : tables data/processed et results du projet 05. Les montants n’ont pas de devise fournie ; les hypothèses de coût ne sont pas des pertes comptables.</div>', unsafe_allow_html=True)
