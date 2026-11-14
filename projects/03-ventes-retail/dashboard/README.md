# Retail Sales Dashboard

Le dossier `dashboard/` contient deux versions cohérentes du même tableau de
bord :

- une version web interactive, consultable dans un navigateur ;
- une application Streamlit exécutable en local.

## Version navigateur

Depuis la racine du projet, lancer :

```bash
python -m http.server 8000
```

Puis ouvrir :

```text
http://localhost:8000/dashboard/web/
```

Le dashboard charge directement
`data/processed/superstore_clean.csv`. Il ne modifie aucune donnée et ne
nécessite aucune bibliothèque JavaScript externe.

La maquette web reprend la structure de référence financière : navigation
verticale sombre, cartes KPI avec mini-tendances, graphique en anneau en haut à
droite, puis deux grands visuels analytiques. Les chiffres sont recalculés à
partir des données réelles du jeu Superstore.

Fonctionnalités disponibles :

- filtres année, région, segment, catégorie et mode de livraison ;
- trois KPI principaux (chiffre d’affaires, profit et marge) avec comparaison
  annuelle et mini-tendances ;
- répartition du chiffre d’affaires par catégorie en anneau ;
- ventes annuelles en colonnes et profit annuel en ligne, avec axes distincts ;
- waterfall mensuel montrant la contribution au profit cumulé, avec total final ;
- infobulles, clics de filtrage sur les visuels et réinitialisation des filtres ;
- disposition responsive pour écran large, tablette et mobile.

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
indicateurs que le dashboard web. Elle s’ouvre normalement à l’adresse
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
