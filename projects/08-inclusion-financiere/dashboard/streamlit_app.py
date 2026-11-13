from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'results'
st.set_page_config(page_title='Fractures d’accès · Global Findex',layout='wide')
st.markdown("""<style>.stApp{background:#f7faf9;color:#173b3b}.hero{background:#fff;border-bottom:3px solid #0f766e;padding:18px 20px;margin:-1rem -1rem 1rem}.hero h1{color:#173b3b;margin:0}.hero p,.note{color:#647878}.kpi,.panel{background:#fff;border:1px solid #dce9e6;border-radius:8px;padding:14px}.kpi{min-height:88px}.kpi small{color:#647878}.kpi b{display:block;color:#173b3b;font-size:1.35rem;margin-top:6px}.stSidebar{background:#eff7f5}</style>""",unsafe_allow_html=True)
def read(name): return pd.read_csv(RES/name)
def chart(fig):
 fig.update_layout(height=320,margin=dict(l=20,r=20,t=35,b=20),paper_bgcolor='white',plot_bgcolor='white',font_color='#173b3b',legend_title_text='',xaxis=dict(gridcolor='#e5efed'),yaxis=dict(gridcolor='#e5efed')); st.plotly_chart(fig,use_container_width=True)
metrics=read('metrics_summary.csv'); trend=read('global_trend.csv'); regional=read('regional_2024.csv'); income=read('income_group_2024.csv'); gender=read('gender_gaps_2024.csv')
def metric(name):
 x=metrics[metrics.metric==name]; return x.iloc[0].value if len(x) else None
with st.sidebar:
 st.markdown('## INCLUSION FINANCE'); page=st.radio('Navigation',['Fractures d’accès','Vue d’ensemble','Comparaison pays','Tendances']); group=st.selectbox('Groupe de revenu',['Tous']+income.incomegroupwb24.astype(str).tolist())
st.markdown('<div class="hero"><h1>Les fractures d’accès</h1><p>Global Findex 2025 · comparer l’accès aux services financiers et les écarts entre groupes</p></div>',unsafe_allow_html=True)
if page=='Fractures d’accès':
 st.subheader('Écarts observés en 2024'); st.markdown('<div class="panel"><span class="note">Les écarts sont descriptifs et ne démontrent pas une causalité.</span></div>',unsafe_allow_html=True); chart(px.histogram(gender,x='account_t_d_men_minus_women',nbins=20,color_discrete_sequence=['#db2777'])); st.dataframe(gender[[c for c in ['countrynewwb','account_t_d_men_minus_women','pop_adult'] if c in gender]],hide_index=True,use_container_width=True)
elif page=='Vue d’ensemble':
 cols=st.columns(4); vals=[('Pays 2024',int(metric('countries_2024'))),('Compte',f"{metric('account_rate_2024'):.1%}"),('Compte bancaire',f"{metric('bank_account_rate_2024'):.1%}"),('Source','Global Findex 2025')]
 for col,(label,value) in zip(cols,vals): col.markdown(f'<div class="kpi"><small>{label}</small><b>{value}</b></div>',unsafe_allow_html=True)
 x=regional if group=='Tous' else income[income.incomegroupwb24==group]; chart(px.bar(x.sort_values('account_t_d'),x='account_t_d',y=x.columns[0],orientation='h',color_discrete_sequence=['#0f766e']))
elif page=='Comparaison pays':
 chart(px.bar(regional,x=regional.columns[0],y=['account_t_d','mobileaccount_t_d'],barmode='group',color_discrete_sequence=['#0f766e','#2563eb'])); st.dataframe(regional,hide_index=True,use_container_width=True)
else:
 chart(px.line(trend,x='year',y=['account_t_d','fiaccount_t_d','mobileaccount_t_d'],markers=True,color_discrete_sequence=['#0f766e','#2563eb','#7c3aed'])); st.dataframe(trend,hide_index=True,use_container_width=True)
st.markdown('<p class="note">Source : Global Findex Database 2025. Les taux agrégés sont pondérés par population adulte couverte.</p>',unsafe_allow_html=True)
