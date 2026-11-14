# Dashboard web — Budget vs réalisé

Version statique du dashboard React, sans backend. Les données sont intégrées au build.

## Ouvrir en local

Depuis la racine du dépôt :

```bash
python -m http.server 8000
```

Ouvrir ensuite `http://localhost:8000/projects/01-budget-vs-actual/dashboard/web/`.

Le build est autonome : les chemins vers `assets/` sont relatifs et aucune ressource externe n’est chargée.

## Reconstruire

Le code source se trouve dans `../../dashboard-web/` :

```bash
cd projects/01-budget-vs-actual/dashboard-web
pnpm install
pnpm build
```

Copier ensuite le contenu de `dist/public/` dans `dashboard/web/` en conservant le fichier `index.html` corrigé.

## Source

City of Austin Open Data Portal, Program Budget Operating Budget Vs Expense Raw Data.
