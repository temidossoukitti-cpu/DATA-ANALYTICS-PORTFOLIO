# Dashboard web — Détection de fraude sur les transactions bancaires

Dashboard interactif sans Power BI : HTML, CSS et JavaScript, sans backend. Trois pages (boutons ronds en haut) :

1. **Vue d'ensemble du risque de fraude** : taux de fraude par fenêtre de 6 h et par tranche de montant, montant frauduleux, filtres.
2. **Scénario : seuil d'alerte et coûts** : trois curseurs (seuil du modèle, coût de friction, sévérité de perte) qui recalculent alertes, précision, rappel et coût estimé contre la référence et contre la règle simple du 99e percentile.
3. **Segmentation et limites des données** : matrice fenêtre × tranche de montant et lacunes de la source.

- **Version hébergée :** https://temidossoukitti-cpu.github.io/DATA-ANALYTICS-PORTFOLIO/projects/05-fraude-bancaire/dashboard/web/
- Les coûts sont des **hypothèses**, pas des pertes comptables. Les montants sont en unités du jeu de données (devise non précisée).

## Ouvrir en local

```bash
python3 -m http.server 8000
```

Puis ouvrir http://localhost:8000/dashboard/web/ (depuis le dossier du projet).

## Régénérer les données du dashboard

```bash
python3 dashboard/build_web_data.py   # lit data/processed et results, écrit dashboard/web/data.js
```

Le script recalcule le coût de référence (14 188,6 unités) et l'affiche à côté de la valeur du dépôt pour contrôle.

## Version Streamlit et rapport

La version [Streamlit](streamlit_app.py) reprend les trois pages du dashboard web : vue d'ensemble, scénario de seuil/coûts et segmentation/limites. Elle utilise les tables `data/processed/` et `results/` comme source unique, avec la palette noire, rouge et gris du dashboard. Installation : `pip install -r dashboard/requirements.txt`, puis `streamlit run dashboard/streamlit_app.py` depuis le dossier du projet.

Le [rapport PDF](reports/dashboard_fraude_report.pdf) présente la question de gestion, les données et limites, la méthode, les résultats, le scénario de seuil et les recommandations. Les coûts y sont explicitement présentés comme des hypothèses.
