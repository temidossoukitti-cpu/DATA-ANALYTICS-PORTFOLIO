# Dashboard web — Analyse financière de Mastercard

Dashboard interactif statique, inspiré de la maquette violette fournie : quatre pages de pilotage financier, sans backend et sans valeur inventée.

1. **Synthèse financière** : produits, résultat net, marges, flux disponible et alertes.
2. **Rentabilité** : résultat d'exploitation, marge nette, ROE, ROA et ratios de rentabilité.
3. **Liquidité & structure** : liquidité courante, trésorerie, endettement et couverture des intérêts.
4. **Trésorerie & croissance** : flux disponible, investissements, croissance des produits et BPA.

- **Version hébergée :** https://temidossoukitti-cpu.github.io/DATA-ANALYTICS-PORTFOLIO/projects/06-analyse-financiere/dashboard/web/
- **Source unique :** `data/processed/` et `results/` du projet 06.
- Les montants sont en USD et les seuils sont des repères internes au projet, pas des normes sectorielles ni une recommandation d'investissement.

## Ouvrir en local

```bash
python3 -m http.server 8000
```

Puis ouvrir `http://localhost:8000/dashboard/web/` depuis le dossier `projects/06-analyse-financiere`.

## Régénérer les données web

```bash
python3 dashboard/build_web_data.py
```

Le script lit les tables annuelles, ratios, alertes et recommandations et écrit `dashboard/web/data.js`.
