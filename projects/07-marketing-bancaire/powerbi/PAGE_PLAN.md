# Plan du dashboard Power BI

Gabarit commun : 1280 × 720, en-tête, navigation latérale, rail de filtres, cinq cartes KPI et bouton de réinitialisation.

## Page 1 — Vue exécutive

Objectif : comprendre le volume de campagne et la conversion. Afficher les cartes Campagnes, Souscriptions, Taux de conversion, Contacts moyens et Part des campagnes déjà contactées. Ajouter une courbe du taux par mois, un histogramme des souscriptions par métier et un segment de mois, canal et résultat précédent.

## Page 2 — Segmentation et efficacité

Objectif : identifier les segments avec un signal de conversion intéressant. Afficher le taux et le volume par groupe d'âge, métier, niveau d'études et résultat de campagne précédente. Les titres doivent rappeler le volume observé et non présenter un segment comme causalement supérieur.

## Page 3 — Priorisation contrôlée

Objectif : comparer la règle simple `poutcome = success` au modèle logistique. Afficher PR-AUC, ROC-AUC, précision, rappel, F1 et le seuil 0,65. Ajouter la courbe précision-rappel et la table de lift par décile. Mentionner que le modèle est une preuve analytique, pas une décision automatique.

## Filtres

Utiliser une seule convention de date : les mois source, sans date civile. Ajouter des filtres sur mois, canal, métier, groupe d'âge et issue précédente. Le bouton Réinitialiser doit restaurer l'état par défaut.
