from pathlib import Path
import json
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
OUT = ROOT / 'results'
PROC = ROOT / 'data' / 'processed'
OUT.mkdir(exist_ok=True)
PROC.mkdir(exist_ok=True)

SOURCE = RAW / 'GlobalFindexDatabase2025.csv'
df = pd.read_csv(SOURCE)
YEARS = [2011, 2014, 2017, 2021, 2024]
INDICATORS = {
    'account_t_d': 'Compte ou mobile money',
    'fiaccount_t_d': 'Compte bancaire / institution financière',
    'mobileaccount_t_d': 'Compte mobile money',
    'fin26a': 'Paiement de factures en ligne',
    'fin26b': 'Achat en ligne',
    'save_any_t_d': 'Épargne',
    'borrow_any_t_d': 'Emprunt',
    'con1': 'Possession d’un téléphone mobile',
    'internet': 'Usage récent d’internet',
}

# Country-level rows are group=all/group2=all. The all-country rows are used for
# country comparisons; aggregate views are calculated using adult-population weights.
country = df[(df.year.isin(YEARS)) & (df.group == 'all') & (df.group2 == 'all')].copy()
country = country[country.codewb.notna()].copy()
country.to_csv(PROC / 'country_indicators.csv', index=False)

# Keep an explicit dictionary for the selected dashboard indicators.
glossary = pd.read_excel(RAW / 'GlobalFindex2025-glossary.xlsx')
glossary['Series_key'] = glossary['Series'].str.replace('.', '_', regex=False)
selected_glossary = glossary[glossary['Series_key'].isin(INDICATORS)].copy()
selected_glossary['dashboard_label'] = selected_glossary['Series_key'].map(INDICATORS)
selected_glossary[['Series_key','dashboard_label','Indicator name','Definition']].to_csv(PROC / 'indicator_dictionary.csv', index=False)

# Weighted average helper. Missing values are excluded from the numerator and denominator.
def weighted_metric(frame, metric, weight='pop_adult'):
    x = frame[[metric, weight]].dropna()
    if x.empty or x[weight].sum() == 0:
        return np.nan
    return float((x[metric] * x[weight]).sum() / x[weight].sum())

# Global / trend series: weighted across countries, avoiding reliance on a single
# precomputed World row for indicators not reported at that aggregate level.
trend_rows = []
for year in YEARS:
    part = country[country.year == year]
    row = {'year': year, 'countries': int(part.codewb.nunique()), 'adult_population_covered': float(part.pop_adult.sum())}
    for metric in INDICATORS:
        row[metric] = weighted_metric(part, metric)
    trend_rows.append(row)
trend = pd.DataFrame(trend_rows)
trend.to_csv(OUT / 'global_trend.csv', index=False)

# Region and income-group views for the latest year, weighted by country adult population.
latest = country[country.year == 2024].copy()
def weighted_group(group_col, output_name):
    rows = []
    for key, part in latest.groupby(group_col, dropna=False):
        row = {group_col: key, 'countries': int(part.codewb.nunique()), 'adult_population_covered': float(part.pop_adult.sum())}
        for metric in INDICATORS:
            row[metric] = weighted_metric(part, metric)
        rows.append(row)
    result = pd.DataFrame(rows).sort_values('account_t_d', ascending=False)
    result.to_csv(OUT / output_name, index=False)
    return result
regional = weighted_group('regionwb24_hi', 'regional_2024.csv')
income = weighted_group('incomegroupwb24', 'income_group_2024.csv')

# Latest country ranking, limited to rows with account data.
rank = latest[['countrynewwb','codewb','regionwb24_hi','incomegroupwb24','pop_adult'] + list(INDICATORS)].copy()
rank = rank.sort_values('account_t_d', ascending=False)
rank.to_csv(OUT / 'country_ranking_2024.csv', index=False)

# Gender and income equity gaps. Positive gender_gap means men report a higher rate.
def group_gap(group_name, labels, output_name, gap_name):
    part = df[(df.year == 2024) & (df.group == group_name) & (df.group2.isin(labels))].copy()
    piv = part.pivot_table(index=['countrynewwb','codewb','regionwb24_hi','incomegroupwb24'], columns='group2', values=list(INDICATORS), aggfunc='first')
    piv.columns = [f'{metric}_{label.replace(" ","_").replace("%","")}' for metric,label in piv.columns]
    piv = piv.reset_index()
    for metric in INDICATORS:
        a, b = labels[0].replace(' ','_').replace('%',''), labels[1].replace(' ','_').replace('%','')
        piv[f'{metric}_{gap_name}'] = piv.get(f'{metric}_{a}', np.nan) - piv.get(f'{metric}_{b}', np.nan)
    base = latest[['codewb','pop_adult']].drop_duplicates('codewb')
    piv = piv.merge(base, on='codewb', how='left')
    piv.to_csv(OUT / output_name, index=False)
    return piv

gender = group_gap('gender', ['men','women'], 'gender_gaps_2024.csv', 'men_minus_women')
income_gap = group_gap('income', ['richest 60%','poorest 40%'], 'income_gaps_2024.csv', 'richest_minus_poorest')

# Segment snapshots for Senegal and selected West African peers, useful for the portfolio narrative.
focus_codes = ['SEN','CIV','BEN','GHA','NGA','KEN','RWA','UGA']
focus = country[(country.year == 2024) & (country.codewb.isin(focus_codes))].copy()
focus.to_csv(OUT / 'focus_countries_2024.csv', index=False)

# QA checks, kept as a small auditable table.
qa = [
    {'rule':'source_rows','value':len(df),'status':'PASS' if len(df)>0 else 'FAIL','note':'CSV officiel Global Findex 2025 chargé.'},
    {'rule':'source_years','value':','.join(map(str,sorted(df.year.dropna().unique()))),'status':'PASS','note':'Les années disponibles sont conservées; l’analyse comparative utilise 2011, 2014, 2017, 2021 et 2024.'},
    {'rule':'country_latest_rows','value':len(latest),'status':'PASS' if len(latest)>=140 else 'WARN','note':'Lignes pays disponibles pour 2024.'},
    {'rule':'duplicate_country_year_all','value':int(country.duplicated(['codewb','year']).sum()),'status':'PASS' if country.duplicated(['codewb','year']).sum()==0 else 'FAIL','note':'Une ligne par pays et année pour la vue nationale.'},
    {'rule':'account_missing_latest','value':int(latest.account_t_d.isna().sum()),'status':'PASS' if latest.account_t_d.isna().sum()==0 else 'WARN','note':'Valeurs manquantes du taux de compte en 2024.'},
]
pd.DataFrame(qa).to_csv(OUT / 'quality_check.csv', index=False)

# Portfolio-level summary metrics for the README/dashboard.
g = trend[trend.year == 2024].iloc[0]
summary = pd.DataFrame([
    ['countries_2024', len(latest), 'countries', 'Country-level rows with group=all in 2024'],
    ['account_rate_2024', g.account_t_d, 'share', 'Weighted adult-population average'],
    ['bank_account_rate_2024', g.fiaccount_t_d, 'share', 'Weighted adult-population average'],
    ['mobile_money_rate_2024', g.mobileaccount_t_d, 'share', 'Weighted adult-population average'],
    ['saving_rate_2024', g.save_any_t_d, 'share', 'Weighted adult-population average'],
    ['borrowing_rate_2024', g.borrow_any_t_d, 'share', 'Weighted adult-population average'],
], columns=['metric','value','unit','definition'])
summary.to_csv(OUT / 'metrics_summary.csv', index=False)

recommendations = pd.DataFrame([
    ['R1','Prioriser l’accès au compte et aux paiements numériques dans les pays où la détention de compte reste faible.','regional_2024.csv','Le taux régional décrit une association descriptive, pas un effet causal.'],
    ['R2','Suivre séparément le compte bancaire et le mobile money : l’inclusion peut progresser par des canaux différents.','global_trend.csv; country_ranking_2024.csv','Les indicateurs ne mesurent pas la qualité, le coût ou la fréquence des services.'],
    ['R3','Mesurer l’écart hommes-femmes et l’écart riches/pauvres avant de conclure à une inclusion équitable.','gender_gaps_2024.csv; income_gaps_2024.csv','Les sous-groupes sont des estimations d’enquête et certaines séries sont indisponibles selon le pays.'],
    ['R4','Utiliser la possession mobile et l’usage d’internet comme prérequis de lecture des paiements digitaux.','regional_2024.csv; income_group_2024.csv','La connectivité n’est pas une preuve d’usage financier.'],
], columns=['id','recommendation','evidence','limitation'])
recommendations.to_csv(OUT / 'recommendations.csv', index=False)

print(json.dumps({'source_rows':len(df),'country_rows':len(country),'latest_countries':len(latest),'outputs':len(list(OUT.glob('*.csv')))}, ensure_ascii=False))
