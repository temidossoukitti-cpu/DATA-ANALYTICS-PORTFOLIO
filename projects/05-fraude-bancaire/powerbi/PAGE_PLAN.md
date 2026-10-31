# Plan des pages Power BI

Le dashboard sera construit par Samuel dans Power BI Desktop; aucun PBIX, PBIP ou export n’est livré à ce stade. Gabarit commun à chaque page : **1280 × 720**, en-tête avec titre-message, navigation latérale sur quatre pages, rail de filtres, cinq cartes KPI, zone visuelle, bouton « Réinitialiser ». Ne choisir ni thème ni couleurs avant la décision commune du portfolio.

## Convention unique de filtre temporel

La source ne contient ni calendrier ni date civile. Utiliser partout le segment `dim_time_window[label_fr]`, trié par `sort_order`, qui filtre des fenêtres relatives de six heures depuis la première transaction. Ne pas ajouter de calendrier ou de slicer de date. Le second segment commun est `dim_amount_band[label_fr]`. `dim_outcome` sert de légende et de contexte analytique, pas de filtre global qui fausserait le dénominateur du taux de fraude.

### Page 1 · Situation de fraude

- **Objectif :** donner en moins d’une minute le niveau de fraude, l’exposition et la qualité du modèle.
- **Cartes (ordre gauche → droite) :** `[Taux de fraude pondéré]`, `[Fraudes estimées]`, `[Exposition fraude estimée]`, `[PR-AUC test]`, `[Coût prévu modèle]`.
- **Visuels (ordre de lecture) :** cartes KPI; colonnes de `[Taux de fraude pondéré]` par bande `dim_amount_band[label_fr]`; colonnes de taux par fenêtre `dim_time_window[label_fr]`; table des montants et expositions légitimes/fraude.
- **Segments :** bande de montant, fenêtre relative de six heures.
- **Titre-message :** « Le taux source est rare; les pertes potentielles doivent être évaluées avec un seuil de contrôle explicite. »

### Page 2 · Segments et exposition

- **Objectif :** décrire où se concentrent la fréquence et l’exposition, sans inventer de type marchand.
- **Cartes :** `[Transactions estimées]`, `[Fraudes estimées]`, `[Taux de fraude pondéré]`, `[Montant estimé]`, `[Exposition fraude estimée]`.
- **Visuels :** colonnes groupées des transactions et fraudes estimées par bande; tableau des quatre bandes avec effectif, taux, montant et exposition fraude; colonnes des taux par fenêtre relative; distribution de `amount` par résultat, pondérée.
- **Segments :** bande de montant, fenêtre relative de six heures; résultat disponible comme légende d’un visuel uniquement.
- **Titre-message :** « Les bandes et périodes décrivent le jeu historique; elles ne constituent pas des causes ni des règles validées. »

### Page 3 · Performance du modèle

- **Objectif :** comparer le modèle test et le score de référence, avec un fort accent sur le rappel et la précision.
- **Cartes :** `[PR-AUC test]`, `[Précision test pondérée]`, `[Rappel test pondéré]`, `[F1 test pondéré]`, `[Seuil recommandé]`.
- **Visuels :** matrice de confusion pondérée (TP/FP/FN/TN); histogramme de `model_probability` par `dim_outcome[label_fr]`; barres de précision, rappel et PR-AUC du modèle et du score montant; table de synthèse avec méthode, seuil et effectifs estimés.
- **Segments :** bande de montant et fenêtre relative; le scorecard du modèle reste filtré sur la partition test.
- **Titre-message :** « Le modèle est évalué sur un test groupé, distinct des données ayant servi au choix du seuil. »

### Page 4 · Décision et hypothèses de coût

- **Objectif :** montrer les compromis entre transactions frauduleuses détectées, fraude manquée et friction légitime.
- **Cartes :** `[Seuil recommandé]`, `[Coût prévu modèle]`, `[Exposition fraude interceptée]`, `[Exposition fraude manquée]`, `[Transactions signalées modèle]`.
- **Visuels :** matrice de chaleur de `model_cost_sensitivity` (sévérité × friction, valeur = coût test); colonnes groupées de `model_money_controls` pour exposition interceptée, exposition manquée et montant légitime signalé; table des hypothèses de coût et de seuil.
- **Segments :** bande de montant et fenêtre relative; aucune unité monétaire ni devise ne doit être ajoutée.
- **Titre-message :** « Le seuil dépend de coûts proxy; valider les pertes nettes et le coût de friction avant une décision opérationnelle. »

Chaque page présente les cinq cartes dans le même ordre que décrit, une hiérarchie typographique identique et un bouton de réinitialisation qui rétablit les filtres de la page; navigation claire entre pages. Les vérifications d’interaction restent à cocher par Samuel dans `qa/INTERACTION_TESTS.md`.
