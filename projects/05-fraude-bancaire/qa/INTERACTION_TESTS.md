# Scénarios d’interaction Power BI

**Statut :** non exécutés. À compléter par Samuel sur le dashboard réel dans Power BI Desktop. Pour chaque scénario, noter le résultat observé et, si nécessaire, le problème à corriger.

| ID | Scénario | Résultat attendu | Statut / note manuelle |
|---|---|---|---|
| INT-01 | Choisir une seule fenêtre relative de six heures sur la page 1. | Les visuels reliés aux faits se filtrent; la fenêtre est clairement relative et aucune date civile n’apparaît. | À tester |
| INT-02 | Sélectionner puis retirer une bande de montant. | Les segments concernés se mettent à jour; les cartes de taux ne divisent pas par zéro. | À tester |
| INT-03 | Combiner une fenêtre et une bande de montant. | Les filtres se cumulent de façon cohérente sur les deux faits reliés. | À tester |
| INT-04 | Cliquer sur une catégorie de résultat dans un visuel de distribution. | Le comportement de surlignage/filtrage est explicite; aucune sélection ne transforme silencieusement le taux global en 100 % ou 0 %. | À tester |
| INT-05 | Appuyer sur « Réinitialiser » après plusieurs filtres. | Les segments de la page reviennent à l’état initial documenté. | À tester |
| INT-06 | Naviguer entre les quatre pages, puis revenir à la page précédente. | La navigation fonctionne et le comportement de persistance des filtres est cohérent avec le plan de page. | À tester |
| INT-07 | Comparer les cartes PR-AUC, précision, rappel et seuil aux fichiers du scorecard. | Les chiffres affichés correspondent au modèle logistique et à la partition test, pas à l’échantillon brut. | À tester |
| INT-08 | Changer la combinaison sévérité/friction de la matrice de sensibilité. | Les valeurs proviennent de `model_cost_sensitivity`; les unités restent celles du dataset. | À tester |
| INT-09 | Vérifier que les libellés d’exposition et de fraude manquée n’emploient pas une devise. | Aucun symbole monétaire ou affirmation de perte réellement recouvrée n’est affiché. | À tester |
| INT-10 | Actualiser depuis un autre emplacement de copie du dépôt en modifiant uniquement `DataFolder`. | Les huit requêtes se chargent sans chemin de machine codé. | À tester |
