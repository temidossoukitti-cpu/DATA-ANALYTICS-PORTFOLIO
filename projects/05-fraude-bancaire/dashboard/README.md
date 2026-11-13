# Dashboard web — détection de fraude bancaire

Dashboard statique interactif en HTML/CSS/JavaScript, construit à partir des résultats versionnés de `results/`. Il comprend quatre vues : Overview, Segments & exposition, Performance modèle, Décision & coûts.

Les montants sont exprimés en unités du dataset, sans symbole monétaire. Les coûts sont des hypothèses proxy et le modèle est présenté comme une file de revue.

Pour reconstruire `web/data.js` :

```bash
python dashboard/build_web_data.py
python3 -m http.server 8000
```

Puis ouvrir `/dashboard/web/`. Le dashboard utilise Chart.js via CDN et ne dépend d’aucun pipeline de préparation.
