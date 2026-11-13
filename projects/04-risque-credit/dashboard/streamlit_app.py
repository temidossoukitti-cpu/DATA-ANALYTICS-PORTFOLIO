from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'results'
st.set_page_config(page_title='Credit Risk · Projet 04',layout='wide')
st.markdown("""<style>.stApp{background:#f5f6fa;color:#25233b}.hero{background:#5b4e8d;color:white;padding:20px 28px;border-radius:0 0 22px 22px;margin:-1rem -1rem 1rem}.hero h1{font-size:2rem;margin:0}.hero p{margin:.3rem 0;color:#e6e1ff}.stMetric,.panel{background:white;border:1px solid #deddea;border-radius:10px;padding:12px}.note{color:#77738a;font-size:.82rem}</style>""",unsafe_allow_html=True)
def read(name): return pd.read_csv(RES/name)
def chart(fig):
 fig.update_layout(height=330,margin=dict(l=20,r=20,t=35,b=20),paper_bgcolor='white',plot_bgcolor='white',font_color='#25233b',legend_title_text=''); st.plotly_chart(fig,use_container_width=True)
portfolio=read('portfolio_kpis.csv').iloc[0]; segments=read('default_by_segment.csv'); bands=read('risk_band_summary.csv'); deciles=read('decile_lift.csv')
with st.sidebar:
 st.markdown('### CREDIT RISK'); page=st.radio('Navigation',['Vue d’ensemble','Segments à risque','Scoring et actions']); risk=st.selectbox('Bande de risque',['Toutes']+bands.risk_band_label.astype(str).tolist())
st.markdown('<div class="hero"><h1>Credit Risk Analysis</h1><p>Portefeuille · risque de défaut · scoring illustratif</p></div>',unsafe_allow_html=True)
if page=='Vue d’ensemble':
 st.subheader('Vue d’ensemble du portefeuille'); cols=st.columns(5); vals=[('Clients',f'{int(portfolio.clients):,}'),('Taux de défaut',f'{portfolio.default_rate:.2%}'),('Limite totale',f'{portfolio.total_credit_limit_ntd:,.0f} NTD'),('Exposition défaut',f'{portfolio.defaulter_credit_limit_exposure_ntd:,.0f} NTD'),('Utilisation moyenne',f'{portfolio.average_utilization:.2%}')]
 for col,(label,value) in zip(cols,vals): col.metric(label,value)
 a,b=st.columns([1.2,.8]);
 with a: st.markdown('<div class="panel"><b>Taux de défaut par bande de risque</b></div>',unsafe_allow_html=True); chart(px.bar(bands,x='risk_band_label',y='default_rate',color_discrete_sequence=['#5b4e8d']))
 with b: st.markdown('<div class="panel"><b>Répartition du portefeuille</b></div>',unsafe_allow_html=True); chart(px.pie(bands,names='risk_band_label',values='customers',hole=.58,color_discrete_sequence=['#5b4e8d','#8176b7','#c4bce8','#d92b2b']))
elif page=='Segments à risque':
 x=segments if risk=='Toutes' else segments[segments.segment_type.astype(str)==risk]; st.subheader('Segments à risque'); chart(px.bar(x.sort_values('default_rate'),x='segment',y='default_rate',color='default_rate',color_continuous_scale='Purples')); st.dataframe(x,hide_index=True,use_container_width=True)
else:
 st.subheader('Scoring et actions'); chart(px.line(deciles,x='decile',y=['default_rate','lift_vs_test_baseline'],markers=True,color_discrete_sequence=['#5b4e8d','#d92b2b'])); st.dataframe(bands,hide_index=True,use_container_width=True)
st.markdown('<p class="note">Les scores et bandes servent au triage illustratif. Ils ne déclenchent pas une décision individuelle.</p>',unsafe_allow_html=True)
