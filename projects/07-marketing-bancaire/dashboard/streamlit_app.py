from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/"results"
st.set_page_config(page_title="Performance marketing d’une banque",layout="wide")
st.markdown("<style>.stApp{background:#f4f4f8;color:#25233b}.hero{background:linear-gradient(135deg,#403566,#5b4e8d);color:white;padding:22px 28px;border-radius:0 0 0 38px;margin:-1rem -1rem 1rem}.kpi{background:white;border:1px solid #deddea;border-radius:10px;padding:12px;min-height:90px}.kpi small{color:#78758c}.kpi b{display:block;font-size:1.35rem;margin:5px 0}.card{background:white;border:1px solid #deddea;border-radius:10px;padding:12px}.note{color:#78758c;font-size:.8rem}</style>",unsafe_allow_html=True)
def read(name): return pd.read_csv(RES/name)
def card(label,value,sub=""):
 st.markdown(f'<div class="kpi"><small>{label}</small><b>{value}</b><span class="note">{sub}</span></div>',unsafe_allow_html=True)
def chart(fig):
 fig.update_layout(height=320,margin=dict(l=20,r=20,t=30,b=20),paper_bgcolor="white",plot_bgcolor="white",font_color="#25233b"); st.plotly_chart(fig,use_container_width=True)

k=read("overall_kpis.csv"); month=read("conversion_by_month.csv"); age=read("conversion_by_age_band.csv"); job=read("conversion_by_job.csv"); model=read("model_scorecard.csv"); dec=read("decile_stats.csv")
with st.sidebar: page=st.radio("Page",["Vue exécutive","Segmentation et efficacité","Priorisation contrôlée"]); month_filter=st.multiselect("Mois",month.label_fr.tolist(),default=month.label_fr.tolist())
st.markdown('<div class="hero"><h1>Performance marketing d’une banque</h1><p>Volume de campagne, conversion et priorisation contrôlée</p></div>',unsafe_allow_html=True)
if page=="Vue exécutive":
 c=st.columns(5); vals=[("Campagnes",k.iloc[0].value),("Souscriptions",k.iloc[1].value),("Conversion",k.iloc[2].value),("Contacts moyens",k.iloc[3].value if len(k)>3 else "—"),("Source","bank-additional-full.csv")];
 for x,(a,b) in zip(c,vals): card(a,b); x
 x=month[month.label_fr.isin(month_filter)]; chart(px.line(x,x="label_fr",y="conversion_rate",markers=True,color_discrete_sequence=["#5b4e8d"])); chart(px.bar(job.sort_values("conversion_rate",ascending=False).head(10),x="label_fr",y="subscriptions",color_discrete_sequence=["#8176b7"]))
elif page=="Segmentation et efficacité":
 chart(px.bar(age,x="label_fr",y="conversion_rate",color="rows",color_continuous_scale="Purples")); st.dataframe(job,hide_index=True,use_container_width=True)
else:
 c=st.columns(5); vals=[("PR-AUC",model.iloc[0].pr_auc_test),("ROC-AUC",model.iloc[0].roc_auc_test),("Précision",model.iloc[0].precision_test),("Rappel",model.iloc[0].recall_test),("Seuil",model.iloc[0].recommended_threshold)];
 for x,(a,b) in zip(c,vals): card(a,b)
 chart(px.line(dec,x="decile",y=["conversion_rate","lift"],markers=True,color_discrete_sequence=["#5b4e8d","#c83455"])); st.dataframe(model,hide_index=True,use_container_width=True)
st.markdown('<div class="note">Le modèle est une preuve analytique et ne constitue pas une décision automatique.</div>',unsafe_allow_html=True)
