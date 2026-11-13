from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dashboard' / 'web' / 'data.js'
R = ROOT / 'results'

def records(name):
    return pd.read_csv(R / name).replace({float('nan'): None}).to_dict('records')

kpi = records('portfolio_kpis.csv')[0]
model = records('model_metrics.csv')[0]
data = {
    'project': '04',
    'title': 'Risque de défaut des cartes de crédit',
    'subtitle': 'Credit Risk Portfolio · données historiques UCI · septembre 2005',
    'kpi': kpi,
    'model': model,
    'metrics': records('metrics_summary.csv'),
    'riskBands': records('risk_band_summary.csv'),
    'segments': records('default_by_segment.csv'),
    'payStatus': records('default_rate_by_pay0.csv'),
    'transitions': records('delinquency_transition.csv'),
    'utilization': records('utilization_summary.csv'),
    'lift': records('decile_lift.csv'),
    'calibration': records('calibration_bins.csv'),
    'loss': records('expected_loss_sensitivity.csv'),
    'coefficients': records('model_coefficients.csv'),
    'recommendations': records('recommendations.csv'),
}
OUT.write_text('window.DASHBOARD_DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
print(f'Generated {OUT}')
