# Périmètre du projet

## 1. Finalité

Le projet **Retail Sales Analysis** fournit une analyse décisionnelle des ventes
afin d'aider une direction commerciale à comprendre la croissance, la
rentabilité et les principaux leviers d'amélioration de la performance.

## 2. Parties prenantes

| Partie prenante | Besoin principal |
|:--|:--|
| Direction générale | Vue synthétique de la performance et des risques |
| Direction commerciale | Pilotage des ventes, remises, clients et territoires |
| Responsables de catégorie | Identification des produits rentables et déficitaires |
| Responsables régionaux | Comparaison des régions et États |
| Équipe Data | Processus reproductible, documenté et contrôlable |
| Finance | Suivi du profit et de la marge |

## 3. Périmètre inclus

### Données

- commandes enregistrées entre 2014 et 2017 ;
- ventes réalisées aux États-Unis ;
- clients, segments et commandes ;
- produits, catégories et sous-catégories ;
- villes, États et régions ;
- chiffre d'affaires, quantités, remises et profit ;
- dates et modes d'expédition.

### Analyses

- évolution annuelle et mensuelle des ventes ;
- évolution du profit et de la marge ;
- performance par catégorie, sous-catégorie et produit ;
- performance par client et segment ;
- performance par région et État ;
- relation descriptive entre remises et rentabilité ;
- analyse synthétique des délais d'expédition ;
- recommandations commerciales.

### Livrables

- fichier de données nettoyé ;
- rapport d'exploration ;
- rapport de nettoyage ;
- dictionnaire de données ;
- méthodologie ;
- documentation du périmètre et des limites ;
- export des KPI ;
- huit visualisations ;
- rapport d'analyse métier ;
- classeur Excel de restitution ;
- README de présentation du projet.

## 4. Périmètre exclu

Les éléments suivants ne font pas partie du projet :

- prévision des ventes futures ;
- modélisation statistique ou machine learning ;
- mesure causale de l'effet des remises ;
- optimisation automatique des prix ;
- calcul détaillé des coûts logistiques ;
- analyse des stocks et ruptures ;
- analyse des retours ou annulations ;
- données concurrentielles ou macroéconomiques ;
- déploiement d'une base de données ;
- dashboard web interactif en production ;
- automatisation planifiée du pipeline.

## 5. Questions métier couvertes

1. Quel niveau de ventes et de profit l'entreprise génère-t-elle ?
2. Comment la performance évolue-t-elle dans le temps ?
3. Quelles catégories et sous-catégories soutiennent la rentabilité ?
4. Quels produits et territoires génèrent des pertes ?
5. Les remises élevées sont-elles associées à une dégradation de la marge ?
6. Le chiffre d'affaires est-il concentré sur quelques clients ?
7. Quelles actions doivent être priorisées par la direction ?

## 6. Critères de réussite

Le projet est considéré comme conforme lorsque :

- la source originale est conservée sans modification ;
- les transformations sont reproductibles par script ;
- les règles de calcul des KPI sont documentées ;
- les agrégats principaux sont rapprochés avec les totaux ;
- chaque visualisation répond à une question métier ;
- les résultats sont disponibles dans des formats accessibles ;
- les limites et hypothèses sont explicitement communiquées ;
- les recommandations sont directement reliées aux résultats observés.

## 7. Période et fréquence

L'analyse couvre les commandes du 3 janvier 2014 au 30 décembre 2017. Le projet
constitue une analyse historique ponctuelle. Aucune fréquence de
rafraîchissement automatique n'est définie.

## 8. Responsabilités

| Domaine | Responsabilité |
|:--|:--|
| Source de données | Fourniture et exactitude des données d'origine |
| Pipeline | Chargement, nettoyage, calcul et export reproductibles |
| Analyse | Interprétation descriptive des résultats |
| Validation métier | Confirmation des doublons potentiels et des règles commerciales |
| Décision | Arbitrage et mise en œuvre des recommandations |

## 9. Gestion des changements

Toute extension du périmètre doit préciser :

- la nouvelle question métier ;
- les données supplémentaires requises ;
- les règles de qualité applicables ;
- l'impact sur les KPI existants ;
- les nouveaux critères de validation ;
- les livrables concernés.

Les modifications de règles de calcul doivent être documentées avant la
comparaison de résultats entre différentes versions.
