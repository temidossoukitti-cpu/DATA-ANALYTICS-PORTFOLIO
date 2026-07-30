# Hypothèses et limites

## 1. Objet du document

Ce document présente les hypothèses retenues pour réaliser l'analyse et les
limites à prendre en compte lors de l'interprétation des résultats.

## 2. Hypothèses de travail

### Granularité

- Chaque ligne représente un produit au sein d'une commande.
- Plusieurs lignes partageant le même `Order ID` appartiennent à une même
  commande.
- `Row ID` est un identifiant technique de ligne et non une mesure métier.

### Mesures financières

- `Sales` représente le chiffre d'affaires net associé à la ligne.
- `Profit` est considéré comme la mesure de résultat disponible et correcte.
- La marge est calculée par `SUM(Profit) / SUM(Sales)`.
- Les montants sont interprétés en dollars américains.
- Aucune conversion monétaire ni correction d'inflation n'est appliquée.

### Clients et produits

- `Customer ID` identifie un client de manière stable sur toute la période.
- `Product ID` identifie un produit pour le calcul du nombre de produits uniques.
- Un client est considéré comme récurrent lorsqu'il a passé plus d'une commande
  distincte sur la période complète.

### Temps et logistique

- `Order Date` est la date de référence pour les analyses temporelles.
- Le délai d'expédition correspond au nombre de jours calendaires entre
  `Order Date` et `Ship Date`.
- Les dates sont supposées exprimées dans un même fuseau horaire.

### Données conservées

- Les deux lignes marquées comme doublons potentiels sont incluses dans tous les
  calculs.
- Les codes postaux sont utilisés comme identifiants et non comme nombres.
- Les zéros initiaux absents des codes postaux ne sont pas reconstitués.

## 3. Limites des données

### Couverture

- Les données couvrent uniquement les États-Unis.
- La période est limitée à 2014-2017.
- Le fichier ne contient pas l'ensemble des facteurs économiques pouvant
  expliquer les ventes.

### Coûts et rentabilité

- Aucun détail sur le coût d'achat, le coût de transport, les frais de stockage,
  les commissions ou les frais administratifs n'est fourni.
- Le calcul du profit ne peut donc pas être audité ou décomposé.
- La rentabilité client complète ne peut pas être mesurée sans coûts de service
  et de fidélisation.

### Cycle commercial

- Les données ne contiennent pas les objectifs de vente.
- Les opportunités perdues et devis non convertis ne sont pas disponibles.
- Les retours, remboursements et annulations ne sont pas identifiés.
- Les canaux de vente et campagnes marketing ne sont pas fournis.

### Produits et stocks

- Aucun niveau de stock ou historique de rupture n'est disponible.
- Les prix catalogue et coûts unitaires ne sont pas fournis.
- Le cycle de vie des produits n'est pas documenté.

### Clients

- Aucune donnée démographique détaillée n'est disponible.
- La date d'acquisition du client n'est pas fournie.
- Le taux de clients récurrents est mesuré sur l'ensemble de la période et ne
  constitue pas un taux de rétention par cohorte.

### Géographie

- Les codes postaux ayant perdu un zéro initial ne sont pas reconstruits.
- L'analyse géographique détaillée au niveau postal peut donc être incomplète.
- Les différences de population, de potentiel de marché et de coût logistique
  entre États ne sont pas normalisées.

## 4. Limites méthodologiques

### Analyse descriptive

L'analyse décrit les relations observées dans les données. Elle ne démontre pas
de relation causale.

Par exemple, les remises élevées sont associées à des marges négatives, mais les
données ne permettent pas d'affirmer que la remise est l'unique cause de la
perte. Le type de produit, la région, le volume ou d'autres facteurs non observés
peuvent également intervenir.

### Agrégation

- Les moyennes calculées au niveau des lignes donnent davantage de poids aux
  commandes contenant plusieurs produits.
- La remise moyenne n'est pas pondérée par le chiffre d'affaires.
- Le délai moyen est calculé au niveau ligne, même si plusieurs lignes peuvent
  appartenir à la même expédition.
- Les classements de produits sont sensibles au niveau de granularité des
  identifiants et libellés.

### Saisonnalité

La période de quatre ans permet d'observer des tendances, mais reste limitée pour
modéliser une saisonnalité durable ou produire des prévisions robustes.

### Valeurs extrêmes

Les valeurs élevées de ventes, profit ou perte sont conservées lorsqu'elles
respectent les règles de cohérence. Elles peuvent influencer certains agrégats
et classements.

## 5. Risques d'interprétation

Les utilisateurs doivent éviter de :

- confondre chiffre d'affaires élevé et rentabilité élevée ;
- appliquer les conclusions à d'autres pays ou périodes sans validation ;
- interpréter une corrélation comme une causalité ;
- supprimer les doublons potentiels sans confirmation métier ;
- comparer les résultats à des données corrigées de l'inflation ;
- considérer le taux de récurrence comme un taux annuel de fidélisation ;
- prendre une décision de prix uniquement à partir de cette analyse.

## 6. Conséquences pour la décision

Les résultats peuvent soutenir la priorisation commerciale, mais les décisions
de prix, de remise, d'assortiment ou de fermeture de marché doivent être
complétées par :

- une analyse des coûts détaillés ;
- la validation des règles de calcul du profit ;
- des données de stock et de logistique ;
- des objectifs commerciaux ;
- une analyse client par cohorte ;
- une validation avec les responsables régionaux et produits.

## 7. Améliorations recommandées

Les prochaines versions du projet pourraient intégrer :

1. les coûts unitaires et logistiques ;
2. les retours et annulations ;
3. les niveaux de stock ;
4. les canaux d'acquisition ;
5. une segmentation RFM des clients ;
6. une analyse causale ou expérimentale des remises ;
7. des prévisions de ventes ;
8. un tableau de bord interactif ;
9. un processus automatisé de contrôle et de rafraîchissement.
