# Dashboard web — projet 07

Dashboard interactif en HTML/CSS/JavaScript sans CDN externe. Les filtres mois source, canal, issue précédente, groupe d’âge et métier recalculent les KPI et visuels sur les données traitées.

- Générer les données : `python3 dashboard/build_web_data.py`
- Ouvrir localement : `python3 -m http.server 8765 --directory dashboard/web`
- Cahier des charges : [`powerbi/PAGE_PLAN.md`](../powerbi/PAGE_PLAN.md)
- Données : `data/processed/fact_campaign.csv` et dimensions associées.
