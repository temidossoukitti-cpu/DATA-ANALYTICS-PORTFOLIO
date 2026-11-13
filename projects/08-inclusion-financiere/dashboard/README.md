# Dashboard — Global Findex 2025

La page d’accueil met l’accent sur les fractures d’accès : différences de détention d’un compte entre hommes et femmes, entre les 60 % les plus riches et les 40 % les plus pauvres, et variations régionales. Les écarts sont calculés à partir des estimations pays 2024, affichés en points de pourcentage et triés selon leur amplitude absolue; leur sens est indiqué dans les libellés.

Les moyennes régionales sont des moyennes simples des écarts observés parmi les pays disposant de données. Les pages « Vue d’ensemble », « Comparaison pays » et « Tendances » donnent le contexte global et restent navigables depuis la barre latérale.

## Exécution locale

Depuis le dossier du projet :

```bash
python3 -m pip install -r requirements.txt
python3 scripts/01_analyze.py
python3 dashboard/build_web_data.py
python3 -m http.server 8000
```

Ouvrir ensuite `http://localhost:8000/dashboard/web/`. La version web est statique; elle charge `dashboard/web/data.js`, généré depuis les tables du dossier `results/`.

Pour re-télécharger les données sources officielles :

```bash
bash scripts/download_source.sh
```

## Calcul des écarts

Pour chaque pays, le taux de détention d’un compte est extrait séparément pour les sous-groupes du Global Findex 2025. Le dashboard calcule la différence signée (hommes moins femmes; plus riches moins plus pauvres), puis classe les pays selon sa valeur absolue. Il ne remplace pas les agrégats officiels de la Banque mondiale et ne permet pas d’inférer une causalité.
## Livrables complémentaires
- `streamlit_app.py` : application interactive cohérente avec le dashboard web.
- `requirements.txt` : dépendances de reproduction.
- `reports/dashboard_inclusion-financiere_report.pdf` : rapport PDF de 5 pages.
- `../preview/dashboard_streamlit.png` : capture de référence.
