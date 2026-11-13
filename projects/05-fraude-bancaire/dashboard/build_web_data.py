from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dashboard' / 'web' / 'data.js'
R = ROOT / 'results'

def records(name):
    return pd.read_csv(R / name).replace({float('nan'): None}).to_dict('records')

def row(name, method=None):
    rows = records(name)
    if method:
        return next(x for x in rows if x.get('method') == method)
    return rows[0]

data = {
    'project': '05',
    'title': 'Détection de fraude bancaire',
    'subtitle': 'Fraud Monitoring · 284 807 transactions · montants en unités du dataset',
    'kpi': records('overall_kpis.csv'),
    'scorecard': records('model_scorecard.csv')[0],
    'modelMetrics': records('model_metrics.csv'),
    'money': records('money_controls.csv'),
    'amountBands': records('fraud_by_amount_band.csv'),
    'timeWindows': records('fraud_by_time_window.csv'),
    'costSensitivity': records('cost_sensitivity.csv'),
    'threshold': records('threshold_curve.csv')[::50],
    'quality': records('quality_check.csv'),
    'recommendations': records('recommendations.csv'),
}
OUT.write_text('window.DASHBOARD_DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
print(f'Generated {OUT}')
