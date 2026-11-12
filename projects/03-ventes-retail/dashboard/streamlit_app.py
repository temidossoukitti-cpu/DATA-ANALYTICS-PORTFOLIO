from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "processed" / "superstore_clean.csv"
NAVY = "#111842"
BLUE = "#536bd5"
RED = "#e64f5d"
GREEN = "#1d9b75"
CATEGORY_COLORS = {
    "Furniture": NAVY,
    "Office Supplies": BLUE,
    "Technology": "#a7b0ec",
}

st.set_page_config(
    page_title="Retail Sales | Executive Performance",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .stApp { background: #f7f7fa; }
      [data-testid="stSidebar"] { background: #242541; }
      [data-testid="stSidebar"] * { color: #f5f5fa; }
      [data-testid="stSidebar"] [data-baseweb="select"] div { color: #25263c; }
      [data-testid="stSidebar"] [data-baseweb="select"] * { color: #25263c !important; }
      [data-testid="stSidebar"] input[role="combobox"] { color: #25263c !important; background: #fff !important; }
      [data-testid="stSidebar"] [data-testid="stSelectbox"] button { color: #25263c !important; background: #fff !important; }
      .block-container { max-width: 1600px; padding-top: 1.25rem; padding-bottom: 1rem; }
      .eyebrow { color: #777989; font-size: .68rem; font-weight: 700; letter-spacing: .13em; }
      .subtle { color: #858694; font-size: .85rem; margin-top: -.5rem; }
      div[data-testid="stMetric"] { background: #fff; border: 1px solid #e7e7ec; border-top: 3px solid #536bd5; border-radius: 6px; padding: 14px 16px; box-shadow: 0 4px 14px #1c1d3010; }
      div[data-testid="stMetric"] label { color: #737584; }
      div[data-testid="stMetricValue"] { color: #20223b; }
      .source-note { color: #9899a6; font-size: .72rem; padding-top: .5rem; }
      [data-testid="stPlotlyChart"] { background: white; border-radius: 5px; }
      @media(max-width:700px){ .block-container{padding-left:1rem;padding-right:1rem;} }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Chargement des données Superstore…")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    return df.dropna(subset=["Order Date", "Sales", "Profit"])


def money(value: float, decimals: int = 0) -> str:
    return f"${value:,.{decimals}f}"


def compact(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.0f}K"
    return money(value)


def style_figure(fig: go.Figure, height: int = 330) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=22, r=20, t=18, b=18),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Segoe UI, Arial, sans-serif", color="#6c6d7c", size=11),
        hoverlabel=dict(bgcolor="#1c1d35", font_color="white"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, linecolor="#e6e6eb")
    fig.update_yaxes(gridcolor="#ededf1", zerolinecolor="#d9d9e0")
    return fig


df = load_data()

with st.sidebar:
    st.markdown("## Retail Sales")
    st.caption("EXECUTIVE PERFORMANCE")
    st.divider()
    st.markdown("### FILTRES")
    years = sorted(df["Year"].dropna().unique().tolist())
    year_choice = st.selectbox("Année", ["Toutes"] + years, index=0)
    region_choice = st.selectbox("Région", ["Toutes"] + sorted(df["Region"].dropna().unique()))
    segment_choice = st.selectbox("Segment", ["Tous"] + sorted(df["Segment"].dropna().unique()))
    category_choice = st.selectbox("Catégorie", ["Toutes"] + sorted(df["Category"].dropna().unique()))
    ship_choice = st.selectbox("Mode de livraison", ["Tous"] + sorted(df["Ship Mode"].dropna().unique()))
    st.divider()
    st.caption("Source : Sample Superstore")
    st.caption("États-Unis · 2014–2017")

filtered = df.copy()
if year_choice != "Toutes":
    filtered = filtered[filtered["Year"] == year_choice]
if region_choice != "Toutes":
    filtered = filtered[filtered["Region"] == region_choice]
if segment_choice != "Tous":
    filtered = filtered[filtered["Segment"] == segment_choice]
if category_choice != "Toutes":
    filtered = filtered[filtered["Category"] == category_choice]
if ship_choice != "Tous":
    filtered = filtered[filtered["Ship Mode"] == ship_choice]

st.markdown('<div class="eyebrow">ANALYSE COMMERCIALE · SUPERSTORE</div>', unsafe_allow_html=True)
st.title("Performance des ventes")
st.markdown('<div class="subtle">Vue exécutive de la performance et de la rentabilité</div>', unsafe_allow_html=True)
st.write("")

if filtered.empty:
    st.warning("Aucune ligne ne correspond à cette sélection.")
    st.stop()

sales = float(filtered["Sales"].sum())
profit = float(filtered["Profit"].sum())
margin = profit / sales if sales else 0.0
orders = int(filtered["Order ID"].nunique())
customers = int(filtered["Customer ID"].nunique())

comparison = df.copy()
if region_choice != "Toutes": comparison = comparison[comparison["Region"] == region_choice]
if segment_choice != "Tous": comparison = comparison[comparison["Segment"] == segment_choice]
if category_choice != "Toutes": comparison = comparison[comparison["Category"] == category_choice]
if ship_choice != "Tous": comparison = comparison[comparison["Ship Mode"] == ship_choice]
latest_year = int(year_choice) if year_choice != "Toutes" else int(filtered["Year"].max())
current_sales = float(comparison.loc[comparison["Year"] == latest_year, "Sales"].sum())
previous_sales = float(comparison.loc[comparison["Year"] == latest_year - 1, "Sales"].sum())
current_profit = float(comparison.loc[comparison["Year"] == latest_year, "Profit"].sum())
previous_profit = float(comparison.loc[comparison["Year"] == latest_year - 1, "Profit"].sum())

def delta_text(current: float, previous: float, label: int) -> str | None:
    if not previous:
        return None
    change = f"{(current - previous) / abs(previous):+.1%}".replace(".", ",")
    return f"{change} vs {label}"

annual_spark = filtered.groupby("Year", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).sort_values("Year")
cols = st.columns([1, 1, 1, 1.15], gap="small")
with cols[0]:
    st.metric("Chiffre d’affaires", money(sales), delta_text(current_sales, previous_sales, latest_year - 1))
with cols[1]:
    st.metric("Profit total", money(profit), delta_text(current_profit, previous_profit, latest_year - 1))
with cols[2]:
    st.metric("Marge bénéficiaire", f"{margin:.1%}".replace(".", ","))
    st.caption(f"{orders:,} commandes · {customers:,} clients")
with cols[3]:
    category = filtered.groupby("Category", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    fig_donut = px.pie(category, names="Category", values="Sales", hole=.64, color="Category", color_discrete_map=CATEGORY_COLORS)
    fig_donut.update_traces(textposition="outside", texttemplate="%{percent:.1%}", hovertemplate="%{label}<br>Ventes : $%{value:,.0f}<br>Part : %{percent}<extra></extra>")
    fig_donut.update_layout(title=dict(text="Ventes par catégorie", x=.02, font=dict(size=14)), showlegend=True, legend=dict(orientation="h", y=-.12, x=.05), margin=dict(l=8,r=8,t=38,b=30), height=230, paper_bgcolor="white", font=dict(size=10))
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

left, right = st.columns([1.12, .88], gap="medium")
with left:
    st.subheader("Ventes et profit par année")
    st.caption("Chiffre d’affaires annuel et profit réalisé · axes distincts")
    annual = filtered.groupby("Year", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).sort_values("Year")
    fig_year = make_subplots(specs=[[{"secondary_y": True}]])
    fig_year.add_trace(go.Bar(x=annual["Year"], y=annual["Sales"], name="Ventes", marker_color=NAVY, hovertemplate="%{x}<br>Ventes : $%{y:,.2f}<extra></extra>"), secondary_y=False)
    fig_year.add_trace(go.Scatter(x=annual["Year"], y=annual["Profit"], name="Profit", mode="lines+markers", line=dict(color=BLUE,width=3), marker=dict(size=7), hovertemplate="%{x}<br>Profit : $%{y:,.2f}<extra></extra>"), secondary_y=True)
    fig_year.update_yaxes(title_text="Ventes · USD", tickprefix="$", tickformat=".2s", secondary_y=False, gridcolor="#ededf1")
    fig_year.update_yaxes(title_text="Profit · USD", tickprefix="$", tickformat=".2s", showgrid=False, secondary_y=True)
    fig_year = style_figure(fig_year, 350)
    st.plotly_chart(fig_year, use_container_width=True, config={"displayModeBar": False})

with right:
    st.subheader("Profit / perte par mois")
    st.caption("Contribution de chaque mois au profit cumulé")
    monthly = filtered.groupby("Month", as_index=False).agg(Profit=("Profit", "sum"), Sales=("Sales", "sum")).sort_values("Month")
    months = monthly["Month"].dt.strftime("%b %y")
    measures = ["relative"] * len(monthly) + ["total"]
    values = monthly["Profit"].tolist() + [float(monthly["Profit"].sum())]
    labels = months.tolist() + ["Total"]
    colors = [BLUE if value >= 0 else RED for value in values[:-1]] + [NAVY]
    fig_waterfall = go.Figure(go.Waterfall(
        x=labels,
        measure=measures,
        y=values,
        increasing={"marker": {"color": BLUE}},
        decreasing={"marker": {"color": RED}},
        totals={"marker": {"color": NAVY}},
        connector={"line": {"color": "#b9bbc8", "width": 1}},
        textposition="none",
        customdata=monthly["Sales"].tolist() + [sales],
        hovertemplate="%{x}<br>Contribution : $%{y:,.2f}<br>Ventes : $%{customdata:,.2f}<extra></extra>",
    ))
    fig_waterfall.update_layout(showlegend=False, xaxis=dict(tickangle=0, tickmode="array", tickvals=labels[::max(1, len(labels)//7)], ticktext=labels[::max(1, len(labels)//7)]), yaxis=dict(tickprefix="$", tickformat=".2s", gridcolor="#ededf1"))
    fig_waterfall = style_figure(fig_waterfall, 350)
    st.plotly_chart(fig_waterfall, use_container_width=True, config={"displayModeBar": False})

start_date = filtered["Order Date"].min().date()
end_date = filtered["Order Date"].max().date()
st.markdown(
    f'<div class="source-note">Source : Sample Superstore · {len(filtered):,} lignes sélectionnées · période {start_date} au {end_date} · marge = profit / chiffre d’affaires.</div>',
    unsafe_allow_html=True,
)
