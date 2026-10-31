# Scénarios d’interaction Power BI

**Statut :** non exécutés. À compléter par Samuel sur le dashboard réel dans Power BI Desktop. Pour chaque scénario, noter le résultat observé et, si nécessaire, le problème à corriger.

| ID | Scénario | Résultat attendu | Statut / note manuelle |
|---|---|---|---|
| INT-01 | Choisir un exercice sur la page 1. | Les cartes et visuels reliés à `fact_financials` et `fact_ratios` se recalculent sur cet exercice; la fiche `financial_scorecard` reste figée sur 2025. | À tester |
| INT-02 | Sélectionner puis retirer la catégorie `Rentabilité`. | Le tableau et les courbes de ratios se filtrent; aucune division par zéro n’apparaît. | À tester |
| INT-03 | Combiner un exercice et une catégorie de ratio. | Les filtres se cumulent de façon cohérente sur `fact_ratios`. | À tester |
| INT-04 | Cliquer sur une année dans un visuel de colonnes. | Le comportement de surlignage/filtrage est explicite; les cartes ne mélangent pas plusieurs exercices. | À tester |
| INT-05 | Appuyer sur « Réinitialiser » après plusieurs filtres. | Les segments de la page reviennent à l’état initial documenté, exercice 2025 inclus. | À tester |
| INT-06 | Naviguer entre les quatre pages, puis revenir à la page précédente. | La navigation fonctionne et le comportement de persistance des filtres est cohérent avec le plan de page. | À tester |
| INT-07 | Comparer les cartes de marge, ROE, ROA et flux disponible aux fichiers `results/`. | Les chiffres affichés correspondent à l’exercice sélectionné et aux valeurs générées, pas à la moyenne de période. | À tester |
| INT-08 | Filtrer `dim_metric[label_fr]` sur un indicateur comptable. | Les visuels du compte de résultat se filtrent sans affecter les ratios, qui dépendent de `dim_ratio`. | À tester |
| INT-09 | Vérifier que les ratios n’affichent pas de devise. | Seuls les montants comptables portent l’unité USD; les ratios restent sans symbole. | À tester |
| INT-10 | Actualiser depuis un autre emplacement de copie du dépôt en modifiant uniquement `DataFolder`. | Les sept requêtes se chargent sans chemin de machine codé. | À tester |
