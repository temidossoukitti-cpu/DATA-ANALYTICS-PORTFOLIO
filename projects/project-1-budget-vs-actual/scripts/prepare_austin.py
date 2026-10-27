from pathlib import Path
import pandas as pd

root = Path('/home/ubuntu/project-1-budget-vs-actual')
raw = root / 'data/raw/austin_budget_vs_expense_full.csv'
processed = root / 'data/processed/austin_budget_vs_actual_prepared.csv'
quality = root / 'checks/data_quality.md'
dictionary = root / 'data/data_dictionary.csv'

df = pd.read_csv(raw)

# Normalisation des textes
text_cols = df.select_dtypes(include=['object']).columns
for col in text_cols:
    df[col] = df[col].astype('string').str.strip()

# Les codes sont des identifiants, pas des montants
for col in ['dept_rollup', 'department_code', 'expense_code']:
    df[col] = df[col].astype('Int64').astype('string')

# Contrôle et calculs financiers
for col in ['budget', 'expenditures']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df['variance'] = df['expenditures'] - df['budget']
df['variance_pct'] = df['variance'].div(df['budget'].where(df['budget'] != 0)).mul(100)
df['budget_zero_flag'] = df['budget'].eq(0)
df['negative_amount_flag'] = df[['budget', 'expenditures']].lt(0).any(axis=1)
df['unfavorable_flag'] = df['variance'].gt(0)
df['period_label'] = 'FY' + df['budget_fiscal_year'].astype('Int64').astype('string') + '-Q' + df['thru_quarter'].astype('Int64').astype('string')

df.to_csv(processed, index=False)

checks = {
    'Lignes brutes': len(pd.read_csv(raw)),
    'Lignes préparées': len(df),
    'Colonnes préparées': len(df.columns),
    'Doublons de lignes': int(df.duplicated().sum()),
    'Clés uniques': int(df['key'].nunique()),
    'Valeurs manquantes budget': int(df['budget'].isna().sum()),
    'Valeurs manquantes dépenses': int(df['expenditures'].isna().sum()),
    'Budgets égaux à zéro': int(df['budget_zero_flag'].sum()),
    'Montants négatifs': int(df['negative_amount_flag'].sum()),
}
quality_lines = ['# Contrôles qualité — Austin Budget vs Actual', '', '| Contrôle | Résultat | Statut |', '|---|---:|:---:|']
for name, value in checks.items():
    critical = name in ['Lignes brutes', 'Lignes préparées', 'Doublons de lignes', 'Valeurs manquantes budget', 'Valeurs manquantes dépenses']
    status = 'PASS' if (value == 0 if critical and 'Lignes' not in name else value > 0) else 'INFO'
    if name == 'Clés uniques':
        status = 'PASS' if value == len(df) else 'FAIL'
    if name == 'Lignes préparées':
        status = 'PASS' if value == checks['Lignes brutes'] else 'FAIL'
    quality_lines.append(f'| {name} | {value:,} | {status} |')
quality_lines += ['', '## Règles appliquées', '', '- Les lignes originales sont conservées ; aucune ligne n’est supprimée automatiquement.', '- `variance` = dépenses réelles − budget.', '- Un écart positif est défavorable pour une dépense, car il signifie que la dépense réelle dépasse le budget.', '- Le pourcentage d’écart n’est pas calculé lorsque le budget vaut zéro, afin d’éviter une division impossible.', '- Les montants négatifs et les budgets nuls sont signalés pour analyse métier, pas corrigés silencieusement.', '']
quality.write_text('\n'.join(quality_lines), encoding='utf-8')

rows = [
    ('budget_fiscal_year', 'Nombre entier', 'Année fiscale du budget'),
    ('thru_quarter', 'Nombre entier', 'Trimestre jusqu’auquel les données sont disponibles'),
    ('dept_rollup_name', 'Texte', 'Grande direction'),
    ('department_name', 'Texte', 'Département'),
    ('fund_name', 'Texte', 'Fonds ou enveloppe financière'),
    ('program_name', 'Texte', 'Programme'),
    ('activity_name', 'Texte', 'Activité'),
    ('unit_name', 'Texte', 'Unité opérationnelle'),
    ('expense_name', 'Texte', 'Catégorie de dépense'),
    ('budget', 'Montant', 'Montant prévu'),
    ('expenditures', 'Montant', 'Montant réellement dépensé'),
    ('variance', 'Montant calculé', 'Dépenses réelles moins budget'),
    ('variance_pct', 'Pourcentage calculé', 'Écart rapporté au budget, non calculé si budget nul'),
    ('budget_zero_flag', 'Oui/Non', 'Indique un budget égal à zéro'),
    ('negative_amount_flag', 'Oui/Non', 'Indique un budget ou une dépense négative'),
    ('unfavorable_flag', 'Oui/Non', 'Indique une dépense réelle supérieure au budget'),
    ('period_label', 'Texte calculé', 'Libellé de la période FY2026-Q3'),
    ('key', 'Identifiant', 'Clé unique de la ligne source'),
]
pd.DataFrame(rows, columns=['column_name', 'type', 'definition']).to_csv(dictionary, index=False)
print(f'prepared_rows={len(df)}')
print(f'prepared_columns={len(df.columns)}')
print(f'variance_total={df["variance"].sum():.2f}')
print(f'zero_budget_rows={int(df["budget_zero_flag"].sum())}')
print(f'negative_amount_rows={int(df["negative_amount_flag"].sum())}')
