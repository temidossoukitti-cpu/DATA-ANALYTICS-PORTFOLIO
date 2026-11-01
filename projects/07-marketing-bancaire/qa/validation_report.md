# Rapport de validation automatisée

Ce rapport est régénéré par `python scripts/run_all.py` à partir de `results/quality_check.csv`, `results/source_integrity.csv`, `results/split_validation.csv` et `results/model_scorecard.csv`.

## État initial observé

- 41 188 lignes et 21 colonnes source.
- Colonnes requises : PASS.
- Valeurs manquantes explicites : PASS ; les modalités `unknown` sont conservées.
- Cible `yes/no` : PASS.
- Bornes âge, campagne, `pdays`, `previous` et indicateurs macroéconomiques : PASS.
- 12 doublons exacts : INFO, conservés et regroupés pour le split.
- 10 700 lignes comportent au moins une modalité `unknown` : INFO, aucune imputation.
- Split train/test : PASS ; fraction test observée 29,999 % contre 30 % demandé.

## Métriques du modèle

Le modèle logistique donne ROC-AUC 0,7917, PR-AUC 0,4518, précision 0,4345, rappel 0,5625 et F1 0,4903 sur l'échantillon test, avec un seuil sélectionné à 0,65 par validation hors pli. Ces métriques ne constituent pas une validation métier ni une autorisation de décision automatisée.

Le contrôle manuel Power BI reste à faire : relations, types, filtres, titres, interactions, export PDF et cohérence des cartes KPI.
