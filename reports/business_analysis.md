# Analyse metier des ventes Retail

## 1. Synthese executive

Le jeu de donnees couvre la periode du **2014-01-03**
au **2017-12-30**. L'entreprise a realise
**$2,297,201** de chiffre d'affaires et
**$286,397** de profit, soit une marge globale de
**12.5%**.

Le chiffre d'affaires progresse sur la periode avec un taux de croissance annuel
compose de **14.8%**. L'annee la plus forte est
**2017**, avec **$733,215** de ventes.
La croissance ne suffit toutefois pas a garantir la rentabilite : certaines
sous-categories, certains Etats et les remises elevees detruisent une part
significative de la marge.

## 2. Indicateurs cles

| KPI | Valeur |
|:--|--:|
| Total Sales | $2,297,200.86 |
| Total Profit | $286,397.02 |
| Profit Margin | 12.5% |
| Orders | 5,009 |
| Customers | 793 |
| Products | 1,862 |
| Units Sold | 37,873 |
| Average Order Value | $458.61 |
| Average Discount | 15.6% |
| Average Shipping Days | 3.96 |
| Repeat Customer Rate | 98.5% |
| Loss-making Sales Share | 20.4% |
| Sales CAGR | 14.8% |
| Latest Annual Sales Growth | 20.4% |
| Latest Annual Profit Growth | 14.2% |

## 3. Evolution du chiffre d'affaires et du profit

| Year | Sales | Profit | Profit Margin | Sales Growth |
|:--|--:|--:|--:|--:|
| 2014 | $484,247 | $49,544 | 10.2% | N/A |
| 2015 | $470,533 | $61,619 | 13.1% | -2.8% |
| 2016 | $609,206 | $81,795 | 13.4% | 29.5% |
| 2017 | $733,215 | $93,439 | 12.7% | 20.4% |

![Performance annuelle](../visuals/01_annual_performance.png)

![Tendance mensuelle](../visuals/02_monthly_sales_trend.png)

Le chiffre d'affaires de la derniere annee progresse de
**20.4%** par rapport a l'annee precedente.
Le profit evolue de **14.2%** sur la meme
periode. Les variations mensuelles restent marquees, ce qui justifie un suivi
du budget et des stocks a une granularite mensuelle.

## 4. Performance des categories et produits

| Category | Sales | Profit | Profit Margin |
|:--|--:|--:|--:|
| Technology | $836,154 | $145,455 | 17.4% |
| Furniture | $742,000 | $18,451 | 2.5% |
| Office Supplies | $719,047 | $122,491 | 17.0% |

![Performance par categorie](../visuals/03_category_performance.png)

La categorie la plus contributrice au profit est **Technology**
avec **$145,455**. La marge la plus faible est celle de
**Furniture** a **2.5%**.

Les trois sous-categories les plus rentables sont
**Copiers, Phones, Accessories**. A l'inverse, les
sous-categories suivantes doivent etre traitees en priorite :

| Sub-Category | Sales | Profit | Profit Margin | Average Discount |
|:--|--:|--:|--:|--:|
| Tables | $206,966 | $-17,725 | -8.6% | 26.1% |
| Bookcases | $114,880 | $-3,473 | -3.0% | 21.1% |
| Supplies | $46,674 | $-1,189 | -2.5% | 7.7% |

![Profit par sous-categorie](../visuals/04_subcategory_profit.png)

Le produit le plus rentable est **Canon imageCLASS 2200 Advanced Copier**
(**$25,200** de profit). Le produit le moins rentable est
**Cubify CubeX 3D Printer Double Head Print**
(**$-8,880**).

## 5. Performance geographique

| Region | Sales | Profit | Profit Margin |
|:--|--:|--:|--:|
| West | $725,458 | $108,418 | 14.9% |
| East | $678,781 | $91,523 | 13.5% |
| Central | $501,240 | $39,706 | 7.9% |
| South | $391,722 | $46,749 | 11.9% |

![Performance regionale](../visuals/05_region_performance.png)

La region **West** apporte le profit le plus eleve avec
**$108,418**. Les cinq Etats les moins rentables sont :

| State | Sales | Profit | Profit Margin |
|:--|--:|--:|--:|
| Texas | $170,188 | $-25,729 | -15.1% |
| Ohio | $78,258 | $-16,971 | -21.7% |
| Pennsylvania | $116,512 | $-15,560 | -13.4% |
| Illinois | $80,166 | $-12,608 | -15.7% |
| North Carolina | $55,603 | $-7,491 | -13.5% |

![Etats les plus et moins rentables](../visuals/07_state_profit_extremes.png)

## 6. Clients

Les **10 premiers clients** representent **6.7%** du chiffre
d'affaires. Le taux de clients ayant passe plus d'une commande est de
**98.5%**.

![Top clients](../visuals/08_top_customers.png)

La concentration limitee du chiffre d'affaires sur les dix premiers clients
reduit la dependance a quelques comptes, mais laisse une opportunite de mieux
segmenter et developper les clients recurrents.

## 7. Remises et rentabilite

![Impact des remises](../visuals/06_discount_profitability.png)

Les ventes accordees avec une remise superieure a 40 % representent
**$128,632** de chiffre d'affaires et generent
**$-99,559** de profit. Le lien observe entre niveau de
remise et marge est descriptif ; il ne prouve pas a lui seul une causalite.

## 8. Recommandations

1. **Encadrer les remises elevees.** Mettre en place un seuil d'approbation et
   suivre la marge attendue avant toute remise superieure a 40 %.
2. **Redresser les sous-categories deficitaires.** Revoir en priorite les prix,
   couts, remises et conditions logistiques de
   **Tables, Bookcases, Supplies**.
3. **Agir sur les zones geographiques en perte.** Construire un plan par Etat
   pour les cinq marches les moins rentables, avec objectifs de marge.
4. **Proteger les moteurs de profit.** Securiser la disponibilite et la
   promotion des sous-categories
   **Copiers, Phones, Accessories**.
5. **Piloter la croissance par la marge.** Completer les objectifs de chiffre
   d'affaires par un objectif de profit et de marge au niveau categorie,
   sous-categorie, region et client.
6. **Developper la fidelisation.** Identifier les clients a forte valeur,
   suivre leur frequence d'achat et proposer des actions ciblees sans remise
   automatique.

## 9. Limites de l'analyse

- Les donnees couvrent uniquement les Etats-Unis et la periode disponible.
- Aucun cout detaille autre que le profit calcule n'est fourni.
- Les deux lignes marquees `Potential Duplicate` sont conservees, conformement
  a la decision de nettoyage ; leur validation metier reste necessaire.
- Les codes postaux ayant perdu un zero initial ne sont pas reconstruits.
- Les conclusions sur les remises sont des associations descriptives.

## 10. Livrables

- Donnees nettoyees : `data/processed/superstore_clean.csv`
- KPI : `data/processed/business_kpis.csv`
- Classeur d'analyse : `reports/retail_sales_analysis.xlsx`
- Graphiques : `visuals/`
