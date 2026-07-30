# Dashboard Power BI - Retail Sales Executive

## 1. Objectif

Ce dashboard est conçu pour le Directeur Commercial. Il permet de suivre le
chiffre d'affaires, la rentabilité, le volume de commandes, le portefeuille
clients et les principaux facteurs de performance.

Le rapport utilise exclusivement
`data/processed/superstore_clean.csv`. Aucune donnée source ou nettoyée ne doit
être modifiée. Le renommage de la requête en `Sales` dans Power BI ne modifie
pas le fichier.

## 2. Livrables

| Fichier | Usage |
|:--|:--|
| `dashboard_design.md` | Spécification fonctionnelle et technique |
| `retail_executive_theme.json` | Thème à importer dans Power BI Desktop |
| `retail_dashboard_background.svg` | Fond de page 16:9 prêt à importer |
| `retail_dashboard_background.png` | Version PNG recommandée du fond de page |
| `measures.dax` | Table calendrier, colonnes et mesures DAX |

Power BI Desktop étant nécessaire pour produire et valider son format binaire
propriétaire, le fichier `.pbix` doit être enregistré depuis Desktop après
assemblage. Les artefacts fournis définissent le design, les mesures, les
positions et les interactions sans altérer les données.

## 3. Direction visuelle

- Format de page : personnalisé, `1440 x 900 px`.
- Style : exécutif, sobre, contrasté et orienté lecture rapide.
- Fond : gris très clair `#F4F6F8`.
- En-tête et rail de filtres : bleu profond `#16324F` / `#203D5A`.
- Ventes : turquoise `#1F7A8C`.
- Profit positif : vert `#2A9D6F`.
- Profit négatif : rouge `#D95D5D`.
- Alerte ou marge intermédiaire : ambre `#E0A458`.
- Typographie : Segoe UI.
- Angles : rayon de 4 à 5 px, sans effets décoratifs excessifs.

Les graphiques sont placés sur le fond SVG avec un arrière-plan transparent.
Leur titre natif est désactivé, car le fond contient déjà les titres.

## 4. Wireframe

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ RETAIL SALES | Executive Performance Dashboard                    USD 2014-17│
├───────────┬───────────┬───────────┬───────────┬───────────┬──────────────────┤
│           │Total Sales│Total Profit│  Margin   │  Orders   │    Customers     │
│  FILTERS  ├──────────────────────────────┬───────────────────────────────────┤
│           │      Sales Trend Monthly     │       Profit Trend Monthly        │
│  Year     │                              │                                   │
│  Region   ├──────────────────┬──────────────────────┬─────────────────────────┤
│  Segment  │Sales by Category │Profit by Sub-Category│    Profit by Region     │
│  Category ├──────────────────────────────┬───────────────────────────────────┤
│  Ship Mode│       Top 10 Customers       │       Discount vs Profit          │
│           │                              │                                   │
└───────────┴──────────────────────────────┴───────────────────────────────────┘
```

## 5. Préparation du modèle

### 5.1 Import

1. Ouvrir Power BI Desktop.
2. Importer `data/processed/superstore_clean.csv` avec **Text/CSV**.
3. Cliquer sur **Transform Data**.
4. Renommer la requête `Sales`.
5. Vérifier les types sans transformer les valeurs :
   - `Order Date`, `Ship Date` : Date ;
   - `Sales`, `Discount`, `Profit` : Decimal number ;
   - `Quantity`, `Row ID` : Whole number ;
   - `Postal Code` : Text ;
   - autres dimensions : Text ;
   - `Potential Duplicate` : True/False.
6. Appliquer les modifications.

### 5.2 Table calendrier

Créer la table `Date` et ses colonnes depuis `measures.dax`, puis :

- créer la relation `Date[Date]` (1) vers `Sales[Order Date]` (*) ;
- direction du filtre : simple, de `Date` vers `Sales` ;
- marquer `Date` comme table de dates avec `Date[Date]` ;
- trier `Date[Month]` par `Date[Month Number]` ;
- trier `Date[Year Month]` par `Date[Year Month Sort]`.

Masquer dans la vue Rapport :

- les identifiants techniques `Row ID`, `Customer ID`, `Product ID` ;
- `Potential Duplicate` ;
- les colonnes de tri `Month Number` et `Year Month Sort`.

## 6. Mesures DAX

Les formules complètes se trouvent dans `measures.dax`.

| Mesure | Formule métier | Format |
|:--|:--|:--|
| `Total Sales` | Somme de `Sales[Sales]` | `$#,0;($#,0);-` |
| `Total Profit` | Somme de `Sales[Profit]` | `$#,0;($#,0);-` |
| `Profit Margin` | `Total Profit / Total Sales` | `0.0%;(0.0%);-` |
| `Orders` | Nombre distinct de `Order ID` | `#,0` |
| `Customers` | Nombre distinct de `Customer ID` | `#,0` |
| `Average Discount` | Moyenne de `Discount` | `0.0%` |
| `Average Order Value` | `Total Sales / Orders` | `$#,0` |
| `Sales LY` | Ventes de la même période N-1 | `$#,0` |
| `Sales YoY` | Variation des ventes vs N-1 | `0.0%` |
| `Profit LY` | Profit de la même période N-1 | `$#,0` |
| `Profit YoY` | Variation du profit vs N-1 | `0.0%` |
| `Customer Sales Rank` | Rang client dans la sélection | Entier |
| `Top 10 Customer Sales` | Ventes si rang inférieur ou égal à 10 | `$#,0` |
| `Profit Status Color` | Vert si profit positif, rouge sinon | Texte |
| `Margin Status Color` | Rouge, ambre ou vert selon la marge | Texte |
| `Selected Period` | Libellé dynamique de la période | Texte |

Contrôles attendus sans filtre :

| KPI | Valeur de contrôle |
|:--|--:|
| Total Sales | `$2,297,200.86` |
| Total Profit | `$286,397.02` |
| Profit Margin | `12.5%` |
| Orders | `5,009` |
| Customers | `793` |

## 7. Liste des visuels et champs

### 7.1 KPI Cards

Créer cinq visuels **Card (new)**.

| Carte | Champ | Position `x,y,w,h` |
|:--|:--|:--|
| Total Sales | `[Total Sales]` | `254, 126, 198, 66` |
| Total Profit | `[Total Profit]` | `492, 126, 198, 66` |
| Profit Margin | `[Profit Margin]` | `730, 126, 198, 66` |
| Orders | `[Orders]` | `968, 126, 198, 66` |
| Customers | `[Customers]` | `1206, 126, 200, 66` |

Format :

- arrière-plan transparent ;
- category label désactivé ;
- callout value 28 px, Segoe UI Semibold ;
- unités `None` pour marge, commandes et clients ;
- unités `Millions`, 2 décimales pour Sales et Profit ;
- couleur conditionnelle du profit via `[Profit Status Color]` ;
- couleur conditionnelle de la marge via `[Margin Status Color]`.

### 7.2 Sales Trend (Monthly)

- Type : **Line chart**.
- Axe X : `Date[Year Month]`.
- Axe Y : `[Total Sales]`.
- Tooltip : `[Total Sales]`, `[Sales LY]`, `[Sales YoY]`, `[Orders]`.
- Position : `254, 270, 550, 182`.
- Couleur : `#1F7A8C`, ligne 3 px, marqueurs désactivés.
- Axe X : continu si `Date[Month Start]` est utilisé, sinon catégoriel.
- Zoom slider : désactivé.

### 7.3 Profit Trend (Monthly)

- Type : **Line chart**.
- Axe X : `Date[Year Month]`.
- Axe Y : `[Total Profit]`.
- Tooltip : `[Total Profit]`, `[Profit LY]`, `[Profit YoY]`,
  `[Profit Margin]`.
- Position : `844, 270, 562, 182`.
- Couleur : `#2A9D6F`.
- Ajouter une ligne constante à `0`, gris `#A7B1BC`.
- Appliquer `[Profit Status Color]` si la version de Power BI permet la couleur
  conditionnelle par point ; sinon conserver le vert et utiliser la ligne zéro.

### 7.4 Sales by Category

- Type : **Donut chart**.
- Legend : `Sales[Category]`.
- Values : `[Total Sales]`.
- Tooltip : `[Total Sales]`, `[Total Profit]`, `[Profit Margin]`, `[Orders]`.
- Position : `254, 530, 345, 132`.
- Couleurs :
  - Technology `#1F7A8C` ;
  - Office Supplies `#2A9D6F` ;
  - Furniture `#E0A458`.
- Detail labels : catégorie + pourcentage du total.
- Inner radius : environ 65 %.

### 7.5 Profit by Sub-Category

- Type : **Clustered bar chart**.
- Axe Y : `Sales[Sub-Category]`.
- Axe X : `[Total Profit]`.
- Tooltip : `[Total Sales]`, `[Total Profit]`, `[Profit Margin]`,
  `[Average Discount]`.
- Position : `639, 530, 445, 132`.
- Tri : `[Total Profit]` décroissant.
- Data colors : `[Profit Status Color]`.
- Axe X : ligne constante à `0`.
- Labels : activés, unités en milliers, 0 décimale.

### 7.6 Profit by Region

- Type : **Clustered bar chart**.
- Axe Y : `Sales[Region]`.
- Axe X : `[Total Profit]`.
- Tooltip : `[Total Sales]`, `[Total Profit]`, `[Profit Margin]`, `[Orders]`.
- Position : `1124, 530, 282, 132`.
- Tri : `[Total Profit]` décroissant.
- Couleur : `#5B6C8F`.
- Labels : activés, unités en milliers.

### 7.7 Top 10 Customers

- Type : **Clustered bar chart**.
- Axe Y : `Sales[Customer Name]`.
- Axe X : `[Top 10 Customer Sales]`.
- Tooltip : `[Total Sales]`, `[Total Profit]`, `[Profit Margin]`, `[Orders]`.
- Filtre visuel : `[Customer Sales Rank]` inférieur ou égal à `10`.
- Position : `254, 740, 550, 126`.
- Tri : `[Top 10 Customer Sales]` décroissant.
- Couleur : `#1F7A8C`.
- Labels : activés, unités en milliers.

Le rang est calculé dans le contexte des slicers. Le Top 10 se recalcule donc
pour chaque année, région, segment, catégorie et mode d'expédition sélectionné.

### 7.8 Discount vs Profit

- Type : **Scatter chart**.
- Axe X : `[Average Discount]`.
- Axe Y : `[Total Profit]`.
- Size : `[Total Sales]`.
- Details : `Sales[Sub-Category]`.
- Legend : `Sales[Category]`.
- Tooltip : `Sales[Sub-Category]`, `[Average Discount]`, `[Total Sales]`,
  `[Total Profit]`, `[Profit Margin]`.
- Position : `844, 740, 562, 126`.
- Axe X : pourcentage, de 0 à 0.70.
- Axe Y : ligne constante à `0`.
- Ajouter une trend line depuis le volet Analytics.
- Transparence des bulles : environ 20 %.

Cette granularité de 17 sous-catégories reste lisible et évite un nuage de
9 994 lignes difficile à interpréter.

## 8. Slicers

Tous les slicers utilisent le style **Dropdown**, avec recherche activée pour
les champs textuels.

| Slicer | Champ | Position `x,y,w,h` | Réglage |
|:--|:--|:--|:--|
| Year | `Date[Year]` | `26, 168, 168, 34` | Multi-select |
| Region | `Sales[Region]` | `26, 250, 168, 34` | Multi-select |
| Segment | `Sales[Segment]` | `26, 332, 168, 34` | Multi-select |
| Category | `Sales[Category]` | `26, 414, 168, 34` | Multi-select |
| Ship Mode | `Sales[Ship Mode]` | `26, 496, 168, 34` | Multi-select |

Format :

- arrière-plan transparent ;
- texte blanc ;
- bordure et titre natifs désactivés ;
- icône dropdown visible ;
- option **Select all** activée ;
- single select désactivé.

Ajouter un bouton **Reset filters** discret sous les slicers uniquement si un
bookmark de réinitialisation est créé. Utiliser l'icône native de gomme ou de
réinitialisation, sans texte long.

## 9. Interactions

### 9.1 Filtres vers visuels

Les cinq slicers filtrent tous les KPI et tous les graphiques.

| Source | Cibles | Interaction |
|:--|:--|:--|
| Year | Tous les visuels | Filter |
| Region | Tous les visuels | Filter |
| Segment | Tous les visuels | Filter |
| Category | Tous les visuels | Filter |
| Ship Mode | Tous les visuels | Filter |

### 9.2 Graphiques entre eux

| Source | Cibles | Interaction |
|:--|:--|:--|
| Sales by Category | Tous sauf lui-même | Filter |
| Profit by Sub-Category | KPI, trends, région, clients, scatter | Filter |
| Profit by Region | KPI, trends, catégorie, sous-catégorie, clients, scatter | Filter |
| Top 10 Customers | KPI, trends, catégorie, sous-catégorie, région, scatter | Filter |
| Discount vs Profit | KPI, trends, catégorie, région, clients | Filter |
| Sales Trend | Autres visuels | Filter |
| Profit Trend | Autres visuels | Filter |

Utiliser **Filter** et non **Highlight** pour garantir que les KPI reflètent
toujours la sélection active. Un clic dans une zone vide annule la sélection.

### 9.3 Comportements particuliers

- Le Top 10 doit rester dynamique grâce à `ALLSELECTED`.
- Les tendances mensuelles doivent conserver les mois sans transaction via
  l'option **Show items with no data** lorsque nécessaire.
- Les tooltips doivent afficher les montants complets, même si les axes utilisent
  des unités abrégées.
- Les valeurs de profit négatives sont rouges dans les barres et les cartes.

## 10. Procédure d'assemblage dans Power BI Desktop

1. Charger le CSV et créer le modèle décrit en section 5.
2. Créer la table, les colonnes et les mesures depuis `measures.dax`.
3. Dans **View > Themes > Browse for themes**, importer
   `retail_executive_theme.json`.
4. Dans **Canvas settings**, choisir `Custom`, largeur `1440`, hauteur `900`.
5. Dans **Canvas background**, importer `retail_dashboard_background.png`,
   choisir `Fit`, transparence `0%`.
6. Ajouter les slicers, cartes et graphiques aux coordonnées indiquées.
7. Désactiver titres, arrière-plans, bordures et visual headers des visuels.
8. Configurer les interactions selon la section 9.
9. Contrôler les cinq KPI globaux avec les valeurs de la section 6.
10. Enregistrer le rapport sous `dashboard/retail_sales_dashboard.pbix`.

## 11. Contrôle qualité final

- Les cinq KPI correspondent aux valeurs de contrôle sans filtre.
- Les commandes et clients utilisent bien `DISTINCTCOUNT`.
- La marge est calculée par `SUM(Profit) / SUM(Sales)`.
- L'axe mensuel est trié chronologiquement.
- Le Top 10 change avec les slicers.
- Le profit négatif est immédiatement identifiable.
- Les interactions ne laissent aucun visuel dans un contexte incohérent.
- Aucun texte ou graphique ne dépasse de son conteneur en vue 16:9.
- Les données source et nettoyées restent inchangées.
