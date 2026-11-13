# Dashboard web interactif

Le dashboard est une page statique sans dépendance de build, mais son interface est active : navigation `Overview`, `Momentum`, `Persona` et `Project info`, filtre d’année, bascule USD/EUR indicative, bascule Wealth/Price, bascule Return/Volatility et sélecteur BTC/ETH dans Momentum.

Depuis le dossier `projects/10-cryptomonnaies`, lancer `python -m http.server 8000`, puis ouvrir `/dashboard/web/`. La page charge `results/dashboard_data.json`. Pour régénérer ce payload après une nouvelle analyse, exécuter `python scripts/build_dashboard_data.py` depuis le dossier du projet.

Le design reprend la référence fournie : fond sombre violet, sidebar persistante, contrôles segmentés, cartes KPI, graphiques lumineux, tableaux compacts et responsive mobile. Les métriques restent calculées sur les données réelles Binance Spot et ne déclenchent aucune transaction.
