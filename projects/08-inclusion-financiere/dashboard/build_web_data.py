from pathlib import Path
import json
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / 'results'
OUT = ROOT / 'dashboard' / 'web' / 'data.js'

def records(name):
    return pd.read_csv(R / name).replace({np.nan: None}).to_dict('records')

summary = records('metrics_summary.csv')
summary_map = {x['metric']: x['value'] for x in summary}
data = {
    'title': 'Inclusion financière',
    'subtitle': 'Global Findex 2025 · Banque mondiale · accès, usage et fracture numérique',
    'summary': summary,
    'summaryMap': summary_map,
    'trend': records('global_trend.csv'),
    'regional': records('regional_2024.csv'),
    'incomeGroups': records('income_group_2024.csv'),
    'ranking': records('country_ranking_2024.csv'),
    'focus': records('focus_countries_2024.csv'),
    'genderGaps': records('gender_gaps_2024.csv'),
    'incomeGaps': records('income_gaps_2024.csv'),
    'recommendations': records('recommendations.csv'),
    'indicators': pd.read_csv(ROOT / 'data' / 'processed' / 'indicator_dictionary.csv').replace({np.nan: None}).to_dict('records'),
}
OUT.write_text('window.DASHBOARD_DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
print(f'Generated {OUT} ({OUT.stat().st_size} bytes)')
