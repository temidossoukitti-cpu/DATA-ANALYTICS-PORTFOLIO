# Plan des pages Power BI

Le dashboard sera construit par Samuel dans Power BI Desktop; aucun PBIX, PBIP ou export n’est livré à ce stade. Gabarit commun à chaque page : **1280 × 720**, en-tête avec titre-message, navigation latérale sur quatre pages, rail de filtres, cinq cartes KPI, zone visuelle, bouton « Réinitialiser ». Ne choisir ni thème ni couleurs avant la décision commune du portfolio.

## Convention unique de filtre temporel

La source est annuelle : utiliser partout le segment `dim_fiscal_year[label_fr]`, trié par `sort_order`, avec sélection simple par défaut sur **Exercice 2025**. Ne pas créer de calendrier quotidien. Le second segment commun est `dim_ratio[category]` sur les pages qui affichent des ratios. `dim_metric[label_fr]` sert de filtre local aux visuels comptables.

Toutes les mesures DAX se recalculent sur l’exercice sélectionné; les cartes de la fiche `financial_scorecard` restent, elles, figées sur le dernier exercice et ne doivent pas être présentées comme filtrées.

### Page 1 · Synthèse financière

- **Objectif :** donner en moins d’une minute le niveau de produits, de résultat, de marge et de flux disponible.
- **Cartes (ordre gauche → droite) :** `[Produits]`, `[Résultat net]`, `[Marge opérationnelle]`, `[Flux de trésorerie disponible]`, `[BPA dilué]`.
- **Visuels (ordre de lecture) :** colonnes des produits et du résultat d’exploitation par exercice; courbe des marges opérationnelle et nette; carte de statut issue de `financial_alerts`.
- **Segments :** exercice.
- **Titre-message :** « Les produits progressent sur la période; la marge opérationnelle reste le premier repère de pilotage. »

### Page 2 · Rentabilité et marges

- **Objectif :** expliquer la formation du résultat et la rentabilité des capitaux.
- **Cartes :** `[Résultat d'exploitation]`, `[Marge nette]`, `[ROE]`, `[ROA]`, `[Taux d'imposition effectif]`.
- **Visuels :** courbes du ROE et du ROA; colonnes de la marge nette; tableau des ratios de la catégorie `Rentabilité` avec valeur récente, moyenne de période et écart.
- **Segments :** exercice, catégorie de ratio limitée à `Rentabilité`.
- **Titre-message :** « Le ROE élevé reflète aussi la faiblesse des capitaux propres; le lire avec le ROA et le levier. »

### Page 3 · Liquidité et structure

- **Objectif :** montrer la capacité à couvrir le passif courant et le niveau d’endettement.
- **Cartes :** `[Ratio de liquidité courante]`, `[Taux d'endettement]`, `[Couverture des intérêts]`, `[Produits]`, `[Résultat net]`.
- **Visuels :** courbes de la liquidité courante et du ratio de trésorerie; colonnes du passif/actif et des capitaux propres/actif; tableau des ratios `Liquidité` et `Structure`.
- **Segments :** exercice, catégorie de ratio limitée à `Liquidité` et `Structure`.
- **Titre-message :** « La liquidité est proche du seuil de 1,0; la structure reste très endettée au sens comptable. »

### Page 4 · Trésorerie et croissance

- **Objectif :** relier la conversion en trésorerie à la croissance et aux investissements.
- **Cartes :** `[Flux de trésorerie disponible]`, `[Marge de flux disponible]`, `[Croissance des produits]`, `[Produits]`, `[BPA dilué]`.
- **Visuels :** colonnes du flux d’exploitation, des investissements et du flux disponible; courbe de la croissance annuelle des produits; tableau des écarts au dernier exercice.
- **Segments :** exercice, métrique de trésorerie.
- **Titre-message :** « La conversion en trésorerie finance la croissance; aucun montant de rachat d’actions n’est disponible dans la source. »

Chaque page présente les cinq cartes dans le même ordre que décrit, une hiérarchie typographique identique et un bouton de réinitialisation qui rétablit les filtres de la page; navigation claire entre pages. Les vérifications d’interaction restent à cocher par Samuel dans `qa/INTERACTION_TESTS.md`.
