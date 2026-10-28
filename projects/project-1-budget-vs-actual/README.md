# Projet 1 — Budget vs Actual Finance Dashboard

## Résumé

Ce projet compare l’argent prévu dans un budget avec l’argent réellement dépensé par la City of Austin. L’objectif est de montrer comment un analyste financier transforme un fichier public en outil d’aide à la décision.

Les données disponibles couvrent l’exercice fiscal 2026 jusqu’au troisième trimestre. Dans ce projet, **budget** signifie montant prévu et **dépenses réelles** signifie montant effectivement dépensé. L’**écart** correspond aux dépenses réelles moins le budget. Pour une dépense, un écart positif signifie un dépassement.

## Question métier

Quels services et quelles catégories de dépenses présentent les plus grandes différences entre le budget prévu et les dépenses réelles ?

## Résultats principaux

Le budget total observé est d’environ 8,10 milliards et les dépenses réelles d’environ 6,02 milliards, soit un taux de consommation de 74,32 %. Aucun département ne présente de dépassement net après regroupement, mais 19 392 lignes individuelles sont au-dessus de leur budget. Cette différence montre pourquoi il faut analyser à la fois le total d’un département et le détail de ses lignes.

Les plus grandes sous-consommations nettes par département concernent Austin Energy, Austin Aviation et G O Debt Service. Une sous-consommation signifie que les dépenses observées sont inférieures au budget ; elle doit être expliquée avant d’être considérée comme une économie réelle.

## Source des données

La source est le dataset officiel [Program Budget Operating Budget Vs Expense Raw Data](https://data.austintexas.gov/Budget-and-Finance/Program-Budget-Operating-Budget-Vs-Expense-Raw-Dat/g5k8-8sud) publié par la City of Austin sur son portail open data. L’export API utilisé est conservé dans `data/raw/austin_budget_vs_expense_full.csv`.

Le fichier brut doit rester inchangé. Le fichier préparé dans `data/processed/` contient les mêmes lignes ainsi que des colonnes calculées pour l’analyse.

## Organisation du projet

| Dossier ou fichier | Utilité |
|---|---|
| `data/raw/` | Fichiers téléchargés tels quels depuis la source officielle |
| `data/processed/` | Fichiers nettoyés et enrichis pour l’analyse |
| `data/data_dictionary.csv` | Explication des colonnes |
| `scripts/` | Programmes reproductibles de téléchargement, contrôle et analyse |
| `sql/model_budget_vs_actual.sql` | Structure SQL et contrôles de base |
| `dashboard/measures.dax` | Formules utilisées dans Power BI |
| `dashboard/austin_budget_vs_actual_model.xlsx` | Modèle Excel avec détail, synthèse et listes de référence |
| `visuals/` | Graphiques générés à partir des données |
| `checks/` | Résultats des contrôles qualité |
| `reports/` | Résultats et management pack |

## Méthode

Les textes ont été nettoyés sans supprimer les lignes. Les codes ont été traités comme des identifiants. Les mesures calculées sont les suivantes :

- `variance` = dépenses réelles − budget ;
- `variance_pct` = écart ÷ budget, lorsque le budget est différent de zéro ;
- `budget_zero_flag` indique un budget nul ;
- `negative_amount_flag` indique un budget ou une dépense négative ;
- `unfavorable_flag` indique une dépense réelle supérieure au budget.

## Contrôles qualité

Le fichier préparé conserve 57 267 lignes. Il ne contient pas de doublon de ligne, les clés sont uniques et les deux colonnes de montant principales ne contiennent pas de valeur vide. Les budgets nuls et les montants négatifs sont signalés, mais non supprimés automatiquement.

## Reproduction

Depuis le dossier du projet, les commandes principales sont :

```bash
python3 scripts/download_austin_full.py
python3 scripts/profile_austin_full.py
python3 scripts/prepare_austin.py
python3 scripts/create_excel_model.py
python3 scripts/analyze_variances.py
```

## Dashboard web

La version interactive est publiée directement dans le navigateur avec GitHub Pages : [ouvrir le dashboard Budget vs Réalisé](https://temidossoukitti-cpu.github.io/Retail-Sales-Analysis/).

Le code source se trouve dans `dashboard-web/`. La publication est automatisée par GitHub Actions à chaque mise à jour du dashboard.

## Limites

Il ne s’agit pas d’une série mensuelle sur plusieurs années. Les résultats décrivent uniquement l’exercice fiscal 2026 jusqu’au troisième trimestre disponible dans l’export. Le dataset concerne une organisation publique et non une entreprise privée. Les lignes avec budget nul ou montant négatif nécessitent une interprétation métier. Le fichier PBIX n’est volontairement pas inclus dans cette version ; la version web interactive est le livrable de visualisation retenu.

## Crédits

Source : City of Austin Open Data Portal. Accès et utilisation selon les conditions indiquées sur la fiche du dataset. Les données ne sont pas synthétiques et aucune conclusion ne doit être attribuée à une entreprise privée.
