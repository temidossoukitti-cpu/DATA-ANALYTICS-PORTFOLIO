# Dashboard web — inclusion financière

Dashboard statique interactif construit avec HTML, CSS et JavaScript à partir des résultats calculés dans `results/`. Il comprend quatre vues : Overview, Comparaison pays, Fractures d’accès et Tendances.

## Reproduire

Depuis le dossier du projet :

```bash
python3 scripts/01_analyze.py
python3 dashboard/build_web_data.py
python3 -m http.server 8000
```

Ouvrir ensuite `http://localhost:8000/dashboard/web/`.

Le dashboard utilise Chart.js depuis un CDN. Les taux régionaux et mondiaux affichés sont des moyennes pondérées par la population adulte couverte et doivent être lus avec les limites documentées dans `data/raw/SOURCE.md`.
