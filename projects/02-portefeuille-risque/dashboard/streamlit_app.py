from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"

def load(name):
    return pd.read_csv(RES / name)

st.set_page_config(page_title="Risque et performance — portefeuille", layout="wide")
st.markdown("""<style>
.block-container{padding:1.2rem 2rem 2rem}.stApp{background:#F3F5F7}
[data-testid="stMetric"]{background:white;border-left:4px solid #176B78;padding:12px 16px;border-radius:5px;box-shadow:0 2px 8px #172B3A12}
h1,h2,h3{color:#172B3A}.small{color:#536572;font-size:.85rem}
</style>""", unsafe_allow_html=True)

metrics = load("metrics_portfolio_vs_index.csv").set_index("Unnamed: 0")
weights = load("weights.csv")
risk = load("risk_contribution.csv")
assets = load("metrics_by_asset.csv")
optw = load("optimization_weights.csv")
frontier = load("efficient_frontier.csv")
perf = load("performance_base100.csv",).assign(date=lambda x: pd.to_datetime(x.date))
summary = load("optimization_summary.csv").rename(columns={"Unnamed: 0":"portefeuille"})

st.title("Risque et performance d'un portefeuille")
st.caption("Executive Analytics Template · Données simulées · 01 nov. 2024 — 23 oct. 2026")

with st.sidebar:
    st.header("Filtres")
    period = st.select_slider("Période", options=["Tout l'historique", "Dernières 52 semaines", "Dernières 26 semaines"], value="Tout l'historique")
    sectors = ["Tous"] + sorted(weights.sector.unique().tolist())
    sector = st.selectbox("Secteur", sectors)
    tickers = ["Tous"] + sorted(weights.ticker.unique().tolist())
    ticker = st.selectbox("Titre", tickers)
    st.divider()
    st.info("Les filtres secteur et titre actualisent les vues de composition. Les KPI de portefeuille restent ceux du portefeuille complet pour éviter une réallocation implicite.")

m = metrics.loc["portefeuille"]
i = metrics.loc["indice_IDX"]
def pct(v): return f"{v:.1%}"
def num(v): return f"{v:,.2f}"

cols = st.columns(6)
labels = [("Rendement annualisé", pct(m.rendement_annualise), f"Indice {pct(i.rendement_annualise)}"), ("Volatilité annualisée", pct(m.volatilite_annualisee), f"Indice {pct(i.volatilite_annualisee)}"), ("Ratio de Sharpe", f"{m.ratio_sharpe:.2f}", f"Indice {i.ratio_sharpe:.2f}"), ("Drawdown maximum", pct(m.drawdown_max), f"Indice {pct(i.drawdown_max)}"), ("Bêta vs IDX", f"{m.beta_vs_IDX:.2f}", "Référence = 1,00"), ("VaR 95 % hebdo", pct(m.VaR_95_hebdo), f"Indice {pct(i.VaR_95_hebdo)}")]
for col,(label,value,sub) in zip(cols,labels):
    with col: st.metric(label,value,sub)

selected = weights.copy()
if sector != "Tous": selected = selected[selected.sector == sector]
if ticker != "Tous": selected = selected[selected.ticker == ticker]
sel_tickers = selected.ticker.tolist()
rf = risk[risk.ticker.isin(sel_tickers)].sort_values("contribution_risque", ascending=False)
wo = optw[optw.ticker.isin(sel_tickers)].copy()
ma = assets[assets.ticker.isin(sel_tickers)].copy()

if period != "Tout l'historique": perf_view = perf.tail(52 if period.endswith("52 semaines") else 26)
else: perf_view = perf

c1,c2 = st.columns([1.1,3.6])
with c1:
    st.subheader("Filtres actifs")
    st.write(f"Secteur : **{sector}**")
    st.write(f"Titre : **{ticker}**")
    st.write(f"{len(selected)} titre(s) sélectionné(s)")
    st.caption("Les données sont simulées et servent à illustrer une méthode d'analyse.")
with c2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=perf_view.date,y=perf_view.portefeuille,name="Portefeuille",line=dict(color="#176B78",width=3)))
    fig.add_trace(go.Scatter(x=perf_view.date,y=perf_view.IDX,name="Indice IDX",line=dict(color="#4F6B78",width=2,dash="dot")))
    fig.update_layout(title="Performance base 100 : portefeuille vs indice",height=300,margin=dict(l=20,r=20,t=45,b=20),paper_bgcolor="white",plot_bgcolor="white",legend=dict(orientation="h"))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

c1,c2 = st.columns(2)
with c1:
    fig=px.bar(rf.sort_values("contribution_risque"),x="contribution_risque",y="ticker",orientation="h",title="Contribution de chaque titre au risque total",labels={"contribution_risque":"Part du risque","ticker":"Titre"},color_discrete_sequence=["#176B78"])
    fig.update_xaxes(tickformat=".0%"); fig.update_layout(height=310,margin=dict(l=20,r=20,t=45,b=20),paper_bgcolor="white",plot_bgcolor="white")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with c2:
    long=wo.melt(id_vars="ticker",value_vars=["actuel","variance_minimale","sharpe_maximal"],var_name="scénario",value_name="poids")
    fig=px.bar(long,x="ticker",y="poids",color="scénario",barmode="group",title="Poids actuels vs portefeuille optimisé",labels={"poids":"Poids","ticker":"Titre","scénario":"Scénario"},color_discrete_sequence=["#176B78","#6B6585","#4D7699"])
    fig.update_yaxes(tickformat=".0%"); fig.update_layout(height=310,margin=dict(l=20,r=20,t=45,b=20),paper_bgcolor="white",plot_bgcolor="white")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

c1,c2=st.columns([1.1,1])
with c1:
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=frontier.volatilite,y=frontier.rendement,mode="lines+markers",name="Frontière",line=dict(color="#176B78",width=3)))
    cur=summary[summary.portefeuille=="actuel"].iloc[0]
    fig.add_trace(go.Scatter(x=[cur.volatilite],y=[cur.rendement],mode="markers",name="Portefeuille actuel",marker=dict(color="#B45454",size=12,symbol="diamond")))
    fig.update_layout(title="Frontière efficiente",height=300,margin=dict(l=20,r=20,t=45,b=20),paper_bgcolor="white",plot_bgcolor="white",xaxis_tickformat=".0%",yaxis_tickformat=".0%")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with c2:
    st.subheader("Top 10 : métriques par titre")
    view=ma.sort_values("ratio_sharpe",ascending=False).copy()
    for col in ["rendement_annualise","volatilite_annualisee","drawdown_max"]: view[col]=view[col].map(pct)
    view["ratio_sharpe"]=view["ratio_sharpe"].map(lambda x:f"{x:.2f}")
    view["beta_vs_IDX"]=view["beta_vs_IDX"].map(lambda x:f"{x:.2f}")
    st.dataframe(view[["ticker","sector","rendement_annualise","volatilite_annualisee","ratio_sharpe","drawdown_max","beta_vs_IDX"]],hide_index=True,use_container_width=True,height=245)

st.caption("Source : résultats versionnés du projet 02 · Données simulées · Les optimisations sont in-sample et ne constituent pas une prévision.")
