# Dictionnaire de données

## 1. Objet du document

Ce document décrit les données utilisées dans le projet **Retail Sales
Analysis**, leur signification métier, leur format et les principales règles de
qualité appliquées.

Le fichier de référence nettoyé est :
`data/processed/superstore_clean.csv`.

## 2. Vue d'ensemble

| Élément | Description |
|:--|:--|
| Source | Sample Superstore |
| Périmètre géographique | États-Unis |
| Période des commandes | 3 janvier 2014 au 30 décembre 2017 |
| Granularité | Une ligne de produit au sein d'une commande |
| Nombre de lignes | 9 994 |
| Colonnes sources | 21 |
| Colonnes après nettoyage | 22 |
| Clé technique de ligne | `Row ID` |
| Identifiant de commande | `Order ID` |
| Encodage source | `latin-1` |
| Encodage du fichier nettoyé | UTF-8 |

Une commande peut contenir plusieurs lignes, car chaque produit commandé
constitue un enregistrement distinct. Les indicateurs relatifs au nombre de
commandes utilisent donc le nombre de valeurs uniques de `Order ID`.

## 3. Dictionnaire des champs

| Champ | Type analytique | Définition métier | Règles et observations |
|:--|:--|:--|:--|
| `Row ID` | Entier | Identifiant technique unique de la ligne source. | Conservé pour la traçabilité. Ne doit pas être agrégé comme une mesure. |
| `Order ID` | Texte | Identifiant de la commande commerciale. | Une commande peut apparaître sur plusieurs lignes. 5 009 commandes uniques. |
| `Order Date` | Date | Date à laquelle la commande a été enregistrée. | Convertie du format source `MM/DD/YYYY` vers `YYYY-MM-DD`. |
| `Ship Date` | Date | Date d'expédition de la commande. | Toujours égale ou postérieure à `Order Date` dans les données contrôlées. |
| `Ship Mode` | Catégorie | Niveau de service utilisé pour l'expédition. | Quatre modalités : Standard Class, Second Class, First Class et Same Day. |
| `Customer ID` | Texte | Identifiant unique du client. | 793 clients uniques. Utilisé pour les mesures de récurrence. |
| `Customer Name` | Texte | Nom complet du client. | Normalisé par suppression des espaces périphériques. |
| `Segment` | Catégorie | Segment commercial du client. | Consumer, Corporate ou Home Office. |
| `Country` | Catégorie | Pays associé à l'adresse de livraison. | Colonne constante : United States. Conservée pour le contexte. |
| `City` | Texte | Ville de livraison. | 531 villes distinctes. |
| `State` | Catégorie | État américain de livraison. | 49 États distincts dans le jeu de données. |
| `Postal Code` | Texte | Code postal de livraison. | Traité comme identifiant. Certains zéros initiaux étaient absents dans la source et n'ont pas été reconstruits. |
| `Region` | Catégorie | Grande région commerciale. | Central, East, South ou West. |
| `Product ID` | Texte | Identifiant commercial du produit. | 1 862 identifiants uniques. |
| `Category` | Catégorie | Famille principale du produit. | Furniture, Office Supplies ou Technology. |
| `Sub-Category` | Catégorie | Sous-famille commerciale du produit. | 17 sous-catégories. |
| `Product Name` | Texte | Libellé détaillé du produit vendu. | 1 850 libellés uniques. Seize valeurs ont été corrigées pour retirer des espaces périphériques. |
| `Sales` | Décimal | Chiffre d'affaires de la ligne de commande, en dollars américains. | Valeurs strictement positives. Agrégée par somme. |
| `Quantity` | Entier | Nombre d'unités vendues sur la ligne. | Valeurs strictement positives. Agrégée par somme. |
| `Discount` | Décimal | Taux de remise appliqué à la ligne. | Valeur comprise entre 0 et 1. Par exemple, `0.20` représente 20 %. |
| `Profit` | Décimal | Profit associé à la ligne, en dollars américains. | Peut être négatif. Agrégé par somme. |
| `Potential Duplicate` | Booléen | Indique si une ligne est identique à une autre sur les variables métier lorsque `Row ID` est exclu. | Champ ajouté pendant le nettoyage. Deux lignes sont signalées, sans suppression automatique. |

## 4. Variables analytiques dérivées

Les champs suivants sont créés en mémoire par `scripts/analyze_sales.py`. Ils ne
sont pas enregistrés dans `superstore_clean.csv`.

| Variable | Formule ou origine | Usage |
|:--|:--|:--|
| `Year` | Année extraite de `Order Date` | Analyse annuelle des ventes et du profit |
| `Month` | Premier jour du mois extrait de `Order Date` | Analyse mensuelle et moyenne mobile |
| `Shipping Days` | `Ship Date - Order Date` | Mesure du délai d'expédition |
| `Profit Margin` | `Profit / Sales` | Comparaison de la rentabilité entre dimensions |
| `Discount Band` | Regroupement de `Discount` | Analyse de la rentabilité par niveau de remise |

Les tranches de remise utilisées sont :

- `0%` ;
- `1-20%` ;
- `21-40%` ;
- `41-60%` ;
- `>60%`.

## 5. Règles d'agrégation

| Mesure | Règle |
|:--|:--|
| Chiffre d'affaires | Somme de `Sales` |
| Profit | Somme de `Profit` |
| Quantités | Somme de `Quantity` |
| Commandes | Nombre distinct de `Order ID` |
| Clients | Nombre distinct de `Customer ID` |
| Produits | Nombre distinct de `Product ID` |
| Remise moyenne | Moyenne arithmétique de `Discount` au niveau des lignes |
| Marge | Somme de `Profit` divisée par somme de `Sales` |
| Panier moyen | Chiffre d'affaires total divisé par nombre de commandes uniques |
| Délai moyen | Moyenne de `Shipping Days` au niveau des lignes |

La marge agrégée n'est pas calculée comme la moyenne des marges de lignes. Cette
méthode évite de donner le même poids à des lignes ayant des montants de ventes
très différents.

## 6. Contrôles de qualité

Les contrôles suivants ont été exécutés :

- validation de la présence des colonnes obligatoires ;
- contrôle des valeurs manquantes ;
- contrôle des doublons stricts ;
- contrôle de l'unicité de `Row ID` ;
- validation du format des dates ;
- recherche de dates d'expédition antérieures aux dates de commande ;
- contrôle des ventes et quantités non positives ;
- contrôle des remises hors de l'intervalle `[0, 1]` ;
- recherche d'espaces périphériques dans les colonnes textuelles ;
- rapprochement des ventes par catégorie avec le chiffre d'affaires total ;
- rapprochement du profit par région avec le profit total.

## 7. Propriété et traçabilité

Le fichier `data/raw/Sample - Superstore.csv` constitue la source immuable du
projet. Le fichier nettoyé est régénéré par `scripts/clean_data.py`. Les règles
de transformation sont détaillées dans
`reports/data_cleaning_report.md`.
