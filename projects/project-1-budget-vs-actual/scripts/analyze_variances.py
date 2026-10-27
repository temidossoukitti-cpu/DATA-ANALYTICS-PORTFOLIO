from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

root = Path('/home/ubuntu/project-1-budget-vs-actual')
df = pd.read_csv(root / 'data/processed/austin_budget_vs_actual_prepared.csv')
visuals = root / 'visuals'
visuals.mkdir(exist_ok=True)

# Synthèses par département et catégorie.
def summarize(group_cols):
    s = df.groupby(group_cols, dropna=False, as_index=False).agg(
        budget=('budget', 'sum'),
        expenditures=('expenditures', 'sum'),
        variance=('variance', 'sum'),
        rows=('key', 'count'),
        zero_budget_rows=('budget_zero_flag', 'sum'),
    )
    s['variance_pct'] = s['variance'].div(s['budget'].where(s['budget'] != 0)).mul(100)
    s['unfavorable'] = s['variance'] > 0
    return s.sort_values('variance', ascending=False)

dep = summarize(['dept_rollup_name', 'department_name'])
cat = summarize(['expense_name'])
dep.to_csv(root / 'data/processed/department_variance_summary.csv', index=False)
cat.to_csv(root / 'data/processed/expense_variance_summary.csv', index=False)

# Graphique 1 : dix plus grandes sous-consommations nettes par département.
top = dep[dep['variance'] < 0].tail(10).sort_values('variance')
plt.figure(figsize=(10, 6))
plt.barh(top['department_name'].str.slice(0, 35), top['variance'] / 1e6, color='#C0504D')
plt.axvline(0, color='#333333', linewidth=0.8)
plt.xlabel('Écart : dépenses réelles moins budget (millions)')
plt.title('10 plus grandes sous-consommations par département — Austin FY2026 Q3')
plt.tight_layout()
plt.savefig(visuals / 'top_10_department_overruns.png', dpi=180)
plt.close()

# Graphique 2 : catégories avec budget non nul et plus grands écarts positifs.
cat_nonzero = cat[(cat['budget'] != 0) & (cat['variance'] > 0)].head(10).sort_values('variance')
if cat_nonzero.empty:
    cat_nonzero = cat[cat['budget'] != 0].head(10).sort_values('variance')
plt.figure(figsize=(10, 6))
plt.barh(cat_nonzero['expense_name'].str.slice(0, 40), cat_nonzero['variance'] / 1e6, color='#D99694')
plt.axvline(0, color='#333333', linewidth=0.8)
plt.xlabel('Écart : dépenses réelles moins budget (millions)')
plt.title('Top 10 des écarts par catégorie — Austin FY2026 Q3')
plt.tight_layout()
plt.savefig(visuals / 'top_10_expense_overruns.png', dpi=180)
plt.close()

# Graphique 3 : budget vs dépenses réelles par grande direction.
roll = df.groupby('dept_rollup_name', as_index=False).agg(budget=('budget','sum'), expenditures=('expenditures','sum'))
roll['total'] = roll['budget'] + roll['expenditures']
roll = roll.sort_values('total', ascending=False).head(12).sort_values('total')
ax = roll.set_index('dept_rollup_name')[['budget', 'expenditures']].div(1e9).plot(kind='barh', figsize=(10, 7), color=['#5B9BD5', '#ED7D31'])
ax.set_xlabel('Montant (milliards)')
ax.set_title('Budget et dépenses réelles par grande direction — Austin FY2026 Q3')
ax.legend(['Budget', 'Dépenses réelles'])
plt.tight_layout()
plt.savefig(visuals / 'budget_vs_actual_by_rollup.png', dpi=180)
plt.close()

# Note de synthèse chiffrée.
total_budget = df['budget'].sum()
total_actual = df['expenditures'].sum()
total_variance = df['variance'].sum()
consumption = total_actual / total_budget if total_budget else None
positive = dep[dep['variance'] > 0]
negative = dep[dep['variance'] < 0]
lines = [
    '# Premiers résultats — Analyse des écarts', '',
    f'- **Budget total observé :** {total_budget:,.2f}',
    f'- **Dépenses réelles totales :** {total_actual:,.2f}',
    f'- **Écart total :** {total_variance:,.2f}',
    f'- **Taux de consommation :** {consumption:.2%}' if consumption is not None else '- **Taux de consommation :** non calculable',
    f'- **Départements en dépassement net :** {len(positive)}',
    f'- **Départements en sous-consommation nette :** {len(negative)}',
    '', '## Trois plus grands dépassements nets par département',
]
for _, r in dep[dep['variance'] < 0].tail(3).sort_values('variance').iterrows():
    lines.append(f'- {r["department_name"]} : écart de {r["variance"]:,.2f}, budget {r["budget"]:,.2f}, dépenses {r["expenditures"]:,.2f}')
line_overruns = int((df['variance'] > 0).sum())
line_underconsumption = int((df['variance'] < 0).sum())
lines[6:6] = [f'- **Lignes individuelles en dépassement :** {line_overruns:,}', f'- **Lignes individuelles en sous-consommation :** {line_underconsumption:,}']
lines[lines.index('## Trois plus grands dépassements nets par département')] = '## Trois plus grands écarts nets par département'
lines += ['', '## Interprétation prudente', '', 'Le total est inférieur au budget, ce qui indique une consommation globale de 74,32 % dans l’extrait. Aucun département ne présente un dépassement net après regroupement, mais certaines lignes individuelles peuvent tout de même dépasser leur budget. Les montants négatifs et les lignes dont le budget est égal à zéro nécessitent une vérification métier avant toute conclusion définitive. Les résultats décrivent l’extrait Austin FY2026 Q3 ; ils ne constituent pas une prévision et ne permettent pas de conclure sur plusieurs années.']
(root / 'reports/first_findings.md').write_text('\n'.join(lines), encoding='utf-8')
print('\n'.join(lines[:12]))
