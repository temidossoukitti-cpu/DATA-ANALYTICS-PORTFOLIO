# Méthodologie d'analyse

## 1. Objectif

La méthodologie définit le processus suivi pour transformer les données de
ventes brutes en informations fiables, reproductibles et exploitables par une
direction commerciale.

Elle repose sur quatre principes :

1. préserver les données originales ;
2. documenter chaque transformation ;
3. rapprocher les indicateurs avec les données sources ;
4. relier chaque analyse à une question métier.

## 2. Processus général

Le projet suit les étapes suivantes :

1. compréhension du besoin métier ;
2. exploration des données ;
3. nettoyage et contrôle de qualité ;
4. documentation des transformations ;
5. construction des indicateurs ;
6. analyse exploratoire et segmentation ;
7. création des visualisations ;
8. interprétation métier ;
9. formulation de recommandations ;
10. validation et export des livrables.

## 3. Compréhension métier

L'analyse vise à expliquer simultanément la croissance et la rentabilité. Le
chiffre d'affaires est donc systématiquement étudié avec le profit, la marge,
les volumes et les remises.

Les axes d'analyse retenus sont :

- le temps ;
- les catégories, sous-catégories et produits ;
- les clients et segments ;
- les régions et États ;
- les niveaux de remise ;
- les modes et délais d'expédition.

## 4. Exploration des données

L'exploration initiale est réalisée sans modifier les données. Elle comprend :

- l'identification des dimensions du fichier ;
- l'analyse des types de données ;
- le calcul des cardinalités ;
- la recherche de valeurs manquantes ;
- la recherche de doublons ;
- l'examen des statistiques numériques ;
- la validation des plages de dates ;
- la détection d'incohérences de format.

Les constats sont consignés dans `reports/data_exploration.md`.

## 5. Nettoyage

Le nettoyage est exécuté par `scripts/clean_data.py`.

### Transformations appliquées

- conversion de `Order Date` et `Ship Date` au format date ;
- conversion de `Postal Code` en texte ;
- suppression des espaces en début et fin des valeurs textuelles ;
- ajout de l'indicateur booléen `Potential Duplicate`.

### Politique de conservation

Aucune ligne n'est supprimée. Les deux lignes identifiées comme doublons
potentiels sont conservées et signalées, car les données disponibles ne
permettent pas de déterminer si elles correspondent à une duplication technique
ou à deux unités commerciales légitimes.

Le fichier source n'est jamais écrasé. Le résultat est enregistré dans
`data/processed/superstore_clean.csv`.

## 6. Construction des KPI

Les KPI sont calculés par `scripts/analyze_sales.py`.

| KPI | Méthode de calcul |
|:--|:--|
| Chiffre d'affaires | `SUM(Sales)` |
| Profit total | `SUM(Profit)` |
| Marge bénéficiaire | `SUM(Profit) / SUM(Sales)` |
| Nombre de commandes | `COUNT DISTINCT(Order ID)` |
| Nombre de clients | `COUNT DISTINCT(Customer ID)` |
| Nombre de produits | `COUNT DISTINCT(Product ID)` |
| Unités vendues | `SUM(Quantity)` |
| Panier moyen | Chiffre d'affaires / commandes uniques |
| Remise moyenne | `AVG(Discount)` au niveau ligne |
| Délai moyen d'expédition | `AVG(Ship Date - Order Date)` |
| Taux de clients récurrents | Clients ayant plus d'une commande / clients |
| Part des ventes à perte | Ventes des lignes à profit négatif / ventes totales |
| CAGR des ventes | Croissance annuelle composée entre 2014 et 2017 |
| Croissance annuelle | Variation par rapport à l'année précédente |

Les résultats sont exportés dans `data/processed/business_kpis.csv`.

## 7. Analyses réalisées

### Analyse temporelle

- chiffre d'affaires annuel ;
- profit annuel ;
- marge annuelle ;
- croissance annuelle ;
- tendance mensuelle ;
- moyenne mobile sur trois mois.

### Analyse produits

- ventes et profit par catégorie ;
- marge par catégorie ;
- rentabilité des sous-catégories ;
- classement des produits par profit.

### Analyse géographique

- ventes, profit et marge par région ;
- classement des États ;
- identification des zones contribuant aux pertes.

### Analyse clients

- chiffre d'affaires par client ;
- part des dix premiers clients ;
- fréquence de commande ;
- taux de clients récurrents ;
- performance par segment.

### Analyse des remises

Les lignes sont regroupées en tranches de remise. Pour chaque tranche, le
chiffre d'affaires, le profit et la marge agrégée sont calculés. Cette analyse
mesure une association descriptive et non un effet causal.

### Analyse logistique

Les commandes sont comparées par mode d'expédition selon le volume, les ventes,
le profit et le délai moyen.

## 8. Visualisation

Chaque graphique répond à une question métier définie :

| Fichier | Question |
|:--|:--|
| `01_annual_performance.png` | Comment les ventes et le profit évoluent-ils par année ? |
| `02_monthly_sales_trend.png` | Quelle est la tendance mensuelle des ventes ? |
| `03_category_performance.png` | Quelles catégories génèrent les ventes et le profit ? |
| `04_subcategory_profit.png` | Quelles sous-catégories créent ou détruisent du profit ? |
| `05_region_performance.png` | Quelles régions sont les plus performantes ? |
| `06_discount_profitability.png` | Comment la marge évolue-t-elle selon la remise ? |
| `07_state_profit_extremes.png` | Quels États contribuent le plus et le moins au profit ? |
| `08_top_customers.png` | Quels clients génèrent le plus de chiffre d'affaires ? |

Les graphiques sont produits avec Matplotlib et enregistrés dans `visuals/`.

## 9. Validation

La validation technique comprend :

- le rechargement du fichier nettoyé après export ;
- le contrôle du nombre de lignes et de colonnes ;
- le contrôle du nombre de valeurs manquantes ;
- le contrôle du nombre de doublons potentiels ;
- le rapprochement du chiffre d'affaires total avec l'agrégation par catégorie ;
- le rapprochement du profit total avec l'agrégation par région ;
- la vérification de la présence de tous les livrables ;
- la vérification de la compilation des scripts Python ;
- l'inspection visuelle des graphiques ;
- la vérification des feuilles et formats du classeur Excel.

## 10. Restitution

Les résultats sont fournis sous plusieurs formats afin de répondre aux besoins
des utilisateurs :

- CSV pour la réutilisation des données ;
- Excel pour l'analyse opérationnelle ;
- PNG pour les présentations ;
- Markdown pour la documentation et GitHub.

Le rapport principal est disponible dans `reports/business_analysis.md`.
