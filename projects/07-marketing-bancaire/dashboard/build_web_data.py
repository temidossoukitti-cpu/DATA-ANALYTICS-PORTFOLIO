from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'data' / 'processed'
OUT = ROOT / 'dashboard' / 'web' / 'data.js'

def labels(name, key):
    df = pd.read_csv(PROC / name)
    return {int(r[key]): str(r['label_fr']) for _, r in df.iterrows()}

age = labels('dim_age_band.csv', 'age_band_key')
job = labels('dim_job.csv', 'job_key')
education = labels('dim_education.csv', 'education_key')
marital = labels('dim_marital.csv', 'marital_key')
month = labels('dim_month.csv', 'month_key')
contact = labels('dim_contact.csv', 'contact_key')
poutcome = labels('dim_poutcome.csv', 'poutcome_key')
campaign = labels('dim_campaign_band.csv', 'campaign_band_key')
outcome = labels('dim_outcome.csv', 'outcome_key')

cols = ['campaign_id','age','age_band_key','job_key','education_key','marital_key','contact_key','month_key','campaign_band_key','previously_contacted','poutcome_key','campaign','outcome_key']
df = pd.read_csv(PROC / 'fact_campaign.csv', usecols=cols)
rows = []
for r in df.to_dict('records'):
    rows.append({
        'id': int(r['campaign_id']), 'age': int(r['age']),
        'ageBand': age.get(int(r['age_band_key']), str(r['age_band_key'])),
        'job': job.get(int(r['job_key']), str(r['job_key'])),
        'education': education.get(int(r['education_key']), str(r['education_key'])),
        'marital': marital.get(int(r['marital_key']), str(r['marital_key'])),
        'contact': contact.get(int(r['contact_key']), str(r['contact_key'])),
        'month': month.get(int(r['month_key']), str(r['month_key'])),
        'campaignBand': campaign.get(int(r['campaign_band_key']), str(r['campaign_band_key'])),
        'previouslyContacted': int(r['previously_contacted']),
        'poutcome': poutcome.get(int(r['poutcome_key']), str(r['poutcome_key'])),
        'campaign': int(r['campaign']),
        'outcome': outcome.get(int(r['outcome_key']), str(r['outcome_key'])),
    })

payload = {'rows': rows, 'labels': {'age': sorted(set(age.values())), 'job': sorted(set(job.values())), 'month': sorted(set(month.values()))}}
OUT.write_text('window.MARKETING_DATA = ' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
print(f'Wrote {len(rows)} rows to {OUT}')
