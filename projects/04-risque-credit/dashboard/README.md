# Dashboard web — risque de défaut des cartes de crédit

Dashboard statique interactif en HTML/CSS/JavaScript, construit à partir des résultats versionnés de `results/`. Il comprend quatre vues : Overview, Segments à risque, Paiements, Scoring & actions.

Les données sont historiques et les seuils de modèle/perte sont illustratifs. Pour reconstruire `web/data.js` :

```bash
python dashboard/build_web_data.py
python3 -m http.server 8000
```

Puis ouvrir `/dashboard/web/`. Le dashboard utilise Chart.js via CDN et ne dépend d’aucun pipeline de préparation.
