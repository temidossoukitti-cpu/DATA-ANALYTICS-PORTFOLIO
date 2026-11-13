from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'results'
st.set_page_config(page_title='Fraud Monitor · Projet 05',layout='wide')
st.markdown("""<style>.stApp{background:#050505;color:#fff}.hero{background:#050505;border-bottom:2px solid #d92b2b;padding:18px 20px;margin:-1rem -1rem 1rem}.hero h1{color:#fff;margin:0}.hero p,.note{color:#8a8a90}.kpi,.panel{background:#141414;border:1px solid #2a2a2e;border-radius:8px;padding:14px}.kpi{min-height:88px}.kpi small{color:#8a8a90}.kpi b{display:block;color:#fff;font-size:1.4rem;margin-top:6px}.stSidebar{background:#0b0b0b}.stSidebar *{color:#fff!important}.stSidebar [data-testid="stMarkdownContainer"] p{color:#8a8a90!important}</style>""",unsafe_allow_html=True)
def read(name): return pd.read_csv(RES/name)
def chart(fig):
 fig.update_layout(height=320,margin=dict(l=20,r=20,t=35,b=20),paper_bgcolor='#141414',plot_bgcolor='#141414',font_color='#fff',legend_title_text='',xaxis=dict(gridcolor='#2a2a2e'),yaxis=dict(gridcolor='#2a2a2e')); st.plotly_chart(fig,use_container_width=True)
k=read('overall_kpis.csv'); amount=read('fraud_by_amount_band.csv'); time=read('fraud_by_time_window.csv'); metrics=read('model_metrics.csv'); curve=read('threshold_curve.csv')
def val(metric):
 x=k[k.metric==metric]; return float(x.iloc[0].value) if len(x) else None
def pct(x): return f'{x:.2%}' if x is not None else '—'
def num(x): return f'{x:,.0f}' if x is not None else '—'
def amount_value(x): return f'{x:,.0f}' if x is not None else '—'
with st.sidebar:
 st.markdown('## FRAUD MONITOR'); page=st.radio('Navigation', ['Vue d’ensemble','Scénario','Segmentation']); band=st.selectbox('Bande de montant',['Toutes']+amount.label_fr.astype(str).tolist())
st.markdown('<div class="hero"><h1>Fraud Monitor</h1><p>Détection de fraude bancaire · surveillance, scénario et segmentation</p></div>',unsafe_allow_html=True)
if page=='Vue d’ensemble':
 cols=st.columns(4); vals=[('Taux de fraude',pct(val('fraud_rate_population_exact'))),('Transactions',num(val('transactions_population_exact'))),('Montant fraude',amount_value(val('fraud_amount_population_exact'))),('PR-AUC',f"{metrics.iloc[0].pr_auc_weighted:.3f}")]
 for col,(label,value) in zip(cols,vals): col.markdown(f'<div class="kpi"><small>{label}</small><b>{value}</b></div>',unsafe_allow_html=True)
 a,b=st.columns(2)
 with a: st.markdown('<div class="panel"><b>Fraude par bande de montant</b></div>',unsafe_allow_html=True); chart(px.bar(amount,x='label_fr',y='fraud_rate',color_discrete_sequence=['#d92b2b']))
 with b: st.markdown('<div class="panel"><b>Fraude par fenêtre temporelle</b></div>',unsafe_allow_html=True); chart(px.bar(time,x='label_fr',y='fraud_rate',color_discrete_sequence=['#d92b2b']))
elif page=='Scénario':
 st.subheader('Scénario de seuil'); chart(px.line(curve,x='threshold',y=['weighted_precision','weighted_recall'],markers=True,color_discrete_sequence=['#d92b2b','#8a8a90'])); st.dataframe(curve,hide_index=True,use_container_width=True)
else:
 st.subheader('Segmentation et exposition'); x=amount if band=='Toutes' else amount[amount.label_fr.astype(str)==band]; chart(px.bar(x,x='label_fr',y=['transactions_estimate','fraud_transactions_estimate'],barmode='group',color_discrete_sequence=['#8a8a90','#d92b2b'])); st.dataframe(x,hide_index=True,use_container_width=True)
 st.markdown('<p class="note">Les coûts éventuels sont des hypothèses proxy documentées dans les résultats et ne sont pas des pertes observées.</p>',unsafe_allow_html=True)
