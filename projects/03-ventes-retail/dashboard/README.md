# Retail Sales Dashboard

Le dossier `dashboard/` contient deux versions cohérentes du même tableau de
bord :

- une version web interactive, consultable dans un navigateur ;
- un kit Power BI prêt à assembler dans Power BI Desktop.

Pour construire la version Power BI sur Windows, suivre le guide détaillé
[`POWER_BI_WINDOWS_GUIDE.md`](POWER_BI_WINDOWS_GUIDE.md) ligne par ligne.

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

## Version Power BI

Power BI Desktop est nécessaire pour produire le fichier binaire `.pbix`.
Les fichiers suivants sont prêts :

| Fichier | Utilisation |
|:--|:--|
| `retail_dashboard_background.png` | Fond de page 1440 x 900 |
| `retail_executive_theme.json` | Thème Power BI |
| `power_query_sales.m` | Import et typage du CSV |
| `measures.dax` | Table calendrier et mesures |
| `dashboard_design.md` | Coordonnées, visuels et interactions |
| `POWER_BI_WINDOWS_GUIDE.md` | Procédure complète à suivre sur Windows |

### Assemblage

1. Ouvrir Power BI Desktop et créer un rapport vide.
2. Dans Power Query, créer un paramètre texte `CsvPath` contenant le chemin
   absolu vers `data/processed/superstore_clean.csv`.
3. Créer une requête vide nommée `Sales`, ouvrir l’éditeur avancé et coller le
   contenu de `power_query_sales.m`.
4. Appliquer les modifications.
5. Créer la table calendrier et les mesures depuis `measures.dax`.
6. Relier `Date[Date]` à `Sales[Order Date]` avec une relation un-à-plusieurs.
7. Importer `retail_executive_theme.json` depuis **View > Themes**.
8. Régler la page sur une taille personnalisée de `1440 x 900`.
9. Ajouter `retail_dashboard_background.png` comme fond avec ajustement
   **Fit** et transparence `0 %`.
10. Ajouter les visuels aux coordonnées de `dashboard_design.md`.
11. Enregistrer le rapport sous `dashboard/retail_sales_dashboard.pbix`.

Valeurs de contrôle sans filtre :

| KPI | Valeur |
|:--|--:|
| Total Sales | 2 297 200,86 $ |
| Total Profit | 286 397,02 $ |
| Profit Margin | 12,5 % |
| Orders | 5 009 |
| Customers | 793 |

Le `.pbix` n’est pas généré automatiquement dans ce dépôt, car sa création et
sa validation nécessitent Power BI Desktop sous Windows.
