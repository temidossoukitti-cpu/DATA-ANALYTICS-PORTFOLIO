# Retail Sales Dashboard

Le dossier `dashboard/` contient deux versions du tableau de bord :

- un **rapport Power BI** au format PBIP (5 pages) : voir [`powerbi/`](powerbi/) et son
  [mode d’emploi](powerbi/README.md) ;
- une application Streamlit exécutable en local.

L’ancienne version web (HTML/JavaScript) a été retirée au profit de Power BI.

Le jeu de données ne fournit pas de budget commercial ni de coûts OPEX
distincts ; les visuels ne prétendent donc pas comparer les ventes à un budget
ni le profit à des charges qui ne figurent pas dans la source.

## Version Streamlit

Depuis la racine du projet, installer les dépendances puis lancer :

```bash
python -m pip install -r requirements.txt
streamlit run dashboard/streamlit_app.py
```

L'application utilise le même CSV nettoyé, les mêmes filtres et les mêmes
indicateurs que le dashboard Power BI. Elle s’ouvre normalement à l’adresse
`http://localhost:8501`.

## Captures et rapport du dashboard

- Rapport PDF : [`reports/retail_dashboard_report.pdf`](reports/retail_dashboard_report.pdf).
- Captures de la vue web et de la vue Streamlit dans [`preview/`](preview/), dont
  les vues globales et filtrées sur la région West.

## Valeurs de contrôle

Sans filtre, les deux versions affichent :
| KPI | Valeur |
|:--|--:|
| Total Sales | 2 297 200,86 $ |
| Total Profit | 286 397,02 $ |
| Profit Margin | 12,5 % |
| Orders | 5 009 |
| Customers | 793 |
