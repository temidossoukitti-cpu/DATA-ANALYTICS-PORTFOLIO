from __future__ import annotations

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
PURPLE, DEEP, ACCENT, BG, INK, MUTED = "#5b4e8d", "#403566", "#c83455", "#f4f4f8", "#25233b", "#78758c"

st.set_page_config(page_title="Mastercard Financial Dashboard", page_icon="◆", layout="wide")
st.markdown(f"""
<style>
.stApp {{ background:{BG}; color:{INK}; }}
[data-testid="stSidebar"] {{ background:#fff; border-right:1px solid #deddea; }}
[data-testid="stSidebar"] * {{ color:{INK} !important; }}
.block-container {{ max-width:1440px; padding-top:1rem; }}
.hero {{ background:linear-gradient(135deg,{DEEP},{PURPLE}); color:#fff; padding:22px 28px 30px; border-radius:0 0 0 42px; margin:-1rem -1rem 1rem; }}
.hero h1 {{ margin:0; font-size:1.65rem; }} .hero p {{ margin:.35rem 0 0; opacity:.83; font-size:.78rem; }}
.kpi {{ background:#fff; border:1px solid #deddea; border-radius:12px; padding:12px 15px; box-shadow:0 4px 14px #33265a12; min-height:94px; }}
.kpi small {{ display:block; color:{MUTED}; font-size:.72rem; }} .kpi b {{ display:block; font-size:1.35rem; margin:.42rem 0; }}
.badge {{ display:inline-block; padding:3px 7px; border-radius:5px; background:#efedf8; color:{PURPLE}; font-size:.68rem; }}
.badge.ok {{ background:#e9f5ee; color:#287c59; }} .badge.warn {{ background:#fbecef; color:{ACCENT}; }}
.card {{ background:#fff; border:1px solid #deddea; border-radius:12px; padding:13px 16px; box-shadow:0 4px 14px #33265a12; }}
.note {{ color:{MUTED}; font-size:.72rem; }} h2 {{ font-size:1.05rem; }} h3 {{ font-size:.9rem; }}
[data-testid="stMetric"] {{ background:#fff; border:1px solid #deddea; border-radius:12px; }}
</style>""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    annual = pd.read_csv(RESULTS / "annual_kpis.csv")
    ratios = pd.read_csv(RESULTS / "ratio_summary.csv")
    alerts = pd.read_csv(RESULTS / "alerts.csv")
    gaps = pd.read_csv(RESULTS / "coverage_gaps.csv")
    recs = pd.read_csv(RESULTS / "recommendations.csv")
    return annual, ratios, alerts, gaps, recs

annual, ratios, alerts, gaps, recs = load_data()
years = annual.fiscal_year.tolist()

def money(x):
    return f"{x/1e9:,.2f} Md USD".replace(",", " ").replace(".", ",")
def pct(x):
    return f"{x*100:.2f}%".replace(".", ",")
def ratio(x):
    return f"{x:.2f}x".replace(".", ",")
def chart_style(fig, height=330):
    fig.update_layout(height=height, margin=dict(l=20,r=20,t=25,b=25), paper_bgcolor="white", plot_bgcolor="white", font=dict(color=INK), showlegend=True, legend=dict(orientation="h", y=1.08))
    fig.update_xaxes(showgrid=False, linecolor="#deddea")
    fig.update_yaxes(gridcolor="#efedf4", linecolor="#deddea")
    return fig

def ratio_table(cats):
    x = ratios[ratios.category.isin(cats)].copy()
    x["2025"] = x.apply(lambda r: pct(r["last_value"]) if r["unit"] == "proportion" else ratio(r["last_value"]), axis=1)
    x["Moyenne"] = x.apply(lambda r: pct(r["mean"]) if r["unit"] == "proportion" else ratio(r["mean"]), axis=1)
    return x[["label_fr","2025","Moyenne","direction"]].rename(columns={"label_fr":"Ratio","direction":"Tendance"})

with st.sidebar:
    st.markdown("## Mastercard")
    st.caption("ANALYSE FINANCIÈRE · PROJET 06")
    st.divider()
    page = st.radio("Navigation", ["Synthèse financière", "Rentabilité", "Liquidité & structure", "Trésorerie & croissance"], label_visibility="collapsed")
    year = st.selectbox("Exercice affiché", ["Période complète"] + years, index=0)
    st.button("Réinitialiser", on_click=lambda: None)
    st.divider()
    st.caption("Source : SEC EDGAR companyfacts")
    st.caption("2019–2025 · 109/109 SQL/Python PASS")
    st.caption("Sans recommandation d'investissement")

r = annual.iloc[-1] if year == "Période complète" else annual[annual.fiscal_year == year].iloc[0]
st.markdown(f'<div class="hero"><h1>Mastercard Financial Dashboard</h1><p>{page} · rentabilité, liquidité, structure, trésorerie et croissance · exercice {int(r.fiscal_year)}</p></div>', unsafe_allow_html=True)

if page == "Synthèse financière":
    cards = [("Produits", money(r.revenue), f"{pct(r.revenue_growth or 0)} vs {int(r.fiscal_year)-1}", "ok"), ("Résultat net", money(r.net_income), f"{pct(r.net_margin)} marge", ""), ("Marge opérationnelle", pct(r.operating_margin), "repère ≥ 40 %", "ok"), ("Flux disponible", money(r.fcf), f"{pct(r.fcf_margin)} des produits", "ok"), ("BPA dilué", f"{r.eps_diluted:.2f} USD", f"{pct(r.eps_growth or 0)} croissance", "")]
    left, right = st.columns([1.3, 1])
    with left:
        st.subheader("Indicateurs clés")
        cols = st.columns(5)
        for c, (lab,val,sub,cl) in zip(cols,cards): c.markdown(f'<div class="kpi"><small>{lab}</small><b>{val}</b><span class="badge {cl}">{sub}</span></div>', unsafe_allow_html=True)
        st.write("")
        st.subheader("Produits et résultat d'exploitation")
        fig = go.Figure([go.Bar(name="Produits", x=annual.fiscal_year, y=annual.revenue/1e9, marker_color=PURPLE), go.Bar(name="Résultat d'exploitation", x=annual.fiscal_year, y=annual.operating_income/1e9, marker_color="#c8c2df")])
        fig.update_yaxes(title="Md USD"); st.plotly_chart(chart_style(fig), width="stretch")
    with right:
        st.subheader("Repères financiers · 2025")
        st.dataframe(alerts[["label_fr","observed","status"]].rename(columns={"label_fr":"Indicateur","observed":"Observé","status":"Statut"}), hide_index=True, width="stretch")
        st.info("Les seuils sont des repères de lecture internes au projet, pas des normes sectorielles.")
    fig = px.line(annual, x="fiscal_year", y=["operating_margin","net_margin"], labels={"value":"Proportion","fiscal_year":"Exercice","variable":"Marge"}, color_discrete_sequence=[PURPLE,ACCENT])
    fig.update_yaxes(tickformat=".0%"); st.subheader("Marges opérationnelle et nette"); st.plotly_chart(chart_style(fig), width="stretch")

elif page == "Rentabilité":
    a,b,c,d,e = st.columns(5)
    vals=[("Résultat d'exploitation",money(r.operating_income),f"{pct(r.operating_margin)} marge"), ("Marge nette",pct(r.net_margin),"résultat net / produits"), ("ROE",pct(r.roe),"à lire avec le ROA"), ("ROA",pct(r.roa),"rentabilité de l'actif"), ("Taux d'impôt",pct(r.effective_tax_rate),"effectif")]
    for col,(lab,val,sub) in zip([a,b,c,d,e],vals): col.markdown(f'<div class="kpi"><small>{lab}</small><b>{val}</b><span class="badge">{sub}</span></div>',unsafe_allow_html=True)
    st.write(""); c1,c2=st.columns([1.2,1])
    with c1:
        st.subheader("ROE et ROA")
        fig=px.line(annual,x="fiscal_year",y=["roe","roa"],labels={"value":"Proportion","fiscal_year":"Exercice","variable":"Ratio"},color_discrete_sequence=[PURPLE,ACCENT]); fig.update_yaxes(tickformat=".0%"); st.plotly_chart(chart_style(fig),width="stretch")
    with c2:
        st.subheader("Lecture de gestion")
        st.markdown(f'<div class="card">Le ROE 2025 atteint <b>{pct(r.roe)}</b>. Il doit être lu avec le ROA ({pct(r.roa)}) et le levier comptable. La marge opérationnelle est de {pct(r.operating_margin)}.</div>',unsafe_allow_html=True)
    st.subheader("Ratios de rentabilité"); st.dataframe(ratio_table(["Rentabilité"]),hide_index=True,width="stretch")

elif page == "Liquidité & structure":
    a,b,c,d,e=st.columns(5); vals=[("Liquidité courante",ratio(r.current_ratio),"repère ≥ 1,0","ok"),("Taux d'endettement",pct(r.debt_ratio),"repère ≤ 80 %","warn"),("Couverture intérêts",ratio(r.interest_coverage),"repère ≥ 8x","ok"),("Produits",money(r.revenue),f"{pct(r.revenue_growth or 0)} croissance",""),("Résultat net",money(r.net_income),pct(r.net_margin)+" marge","")]
    for col,(lab,val,sub,cl) in zip([a,b,c,d,e],vals): col.markdown(f'<div class="kpi"><small>{lab}</small><b>{val}</b><span class="badge {cl}">{sub}</span></div>',unsafe_allow_html=True)
    st.write(""); c1,c2=st.columns(2)
    with c1:
        fig=px.line(annual,x="fiscal_year",y=["current_ratio","cash_ratio"],labels={"value":"Ratio","fiscal_year":"Exercice","variable":"Ratio"},color_discrete_sequence=[PURPLE,"#8176b7"]); st.subheader("Liquidité courante et ratio de trésorerie"); st.plotly_chart(chart_style(fig),width="stretch")
    with c2:
        fig=px.bar(annual,x="fiscal_year",y="debt_ratio",labels={"debt_ratio":"Passif / actif","fiscal_year":"Exercice"},color_discrete_sequence=[PURPLE]); fig.update_yaxes(tickformat=".0%"); st.subheader("Structure du bilan"); st.plotly_chart(chart_style(fig),width="stretch")
    st.subheader("Ratios de liquidité et de structure"); st.dataframe(ratio_table(["Liquidité","Structure"]),hide_index=True,width="stretch")

else:
    a,b,c,d,e=st.columns(5); vals=[("Flux disponible",money(r.fcf),pct(r.fcf_margin)+" des produits","ok"),("Marge FCF",pct(r.fcf_margin),"conversion en cash",""),("Croissance produits",pct(r.revenue_growth or 0),"variation annuelle","ok"),("Produits",money(r.revenue),f"exercice {r.fiscal_year}",""),("BPA dilué",f"{r.eps_diluted:.2f} USD",pct(r.eps_growth or 0)+" croissance","")]
    for col,(lab,val,sub,cl) in zip([a,b,c,d,e],vals): col.markdown(f'<div class="kpi"><small>{lab}</small><b>{val}</b><span class="badge {cl}">{sub}</span></div>',unsafe_allow_html=True)
    st.write(""); c1,c2=st.columns([1.2,1])
    with c1:
        st.subheader("Flux d'exploitation, investissements et flux disponible")
        fig=go.Figure([go.Bar(name="Flux d'exploitation",x=annual.fiscal_year,y=annual.cfo/1e9,marker_color=PURPLE),go.Bar(name="Investissements",x=annual.fiscal_year,y=annual.capex/1e9,marker_color="#d7d3e7"),go.Bar(name="Flux disponible",x=annual.fiscal_year,y=annual.fcf/1e9,marker_color=ACCENT)]); fig.update_yaxes(title="Md USD"); st.plotly_chart(chart_style(fig),width="stretch")
    with c2:
        st.subheader("Croissance annuelle des produits")
        fig=px.line(annual,x="fiscal_year",y="revenue_growth",labels={"revenue_growth":"Croissance","fiscal_year":"Exercice"},color_discrete_sequence=[PURPLE]); fig.update_yaxes(tickformat=".0%"); st.plotly_chart(chart_style(fig),width="stretch")
    st.subheader("Indicateurs de trésorerie"); out=annual[["fiscal_year","fcf","fcf_margin","capex_intensity"]].copy(); out["fcf"]=out.fcf.map(money); out["fcf_margin"]=out.fcf_margin.map(pct); out["capex_intensity"]=out.capex_intensity.map(pct); st.dataframe(out.rename(columns={"fiscal_year":"Exercice","fcf":"Flux disponible","fcf_margin":"Marge FCF","capex_intensity":"Intensité capex"}),hide_index=True,width="stretch")

st.markdown('<div class="note">Source : tables results/ du projet 06. Montants en USD. Les seuils sont internes au projet et cette analyse ne constitue pas une recommandation d’investissement.</div>',unsafe_allow_html=True)
