# Modèle de données

## Tables et clés

`fact_clients` contient une ligne par client et la cible `default_next_month`. Sa clé primaire est `client_id`; cette clé technique n’est jamais utilisée comme variable prédictive. Les clés étrangères sont `age_band_key`, `education_key`, `marriage_key`, `limit_band_key`, `pay_status_key` et `risk_band_key`. Le fait conserve les champs financiers, historiques de paiement, variables dérivées et la partition `Train` ou `Test`.

| Table | Clé primaire | Libellé / contenu | Cardinalité vers le fait |
|---|---|---|---|
| `dim_age_band` | `age_band_key` | Bandes d’âge descriptives ordonnées | 1 → plusieurs |
| `dim_education` | `education_key` | Catégories recodées d’éducation | 1 → plusieurs |
| `dim_marriage` | `marriage_key` | Catégories recodées d’état matrimonial | 1 → plusieurs |
| `dim_limit_band` | `limit_band_key` | Quintiles de limite et bornes observées | 1 → plusieurs |
| `dim_pay_status` | `pay_status_key` | Code et libellé du statut `pay_0` | 1 → plusieurs |
| `dim_risk_band` | `risk_band_key` | Bande de probabilité et bornes | 1 → plusieurs |

Créer dans Power BI six relations actives, un-à-plusieurs, avec filtrage simple de la dimension vers `fact_clients`. Les clés étrangères et valeurs de dimension sont vérifiées lors de la reconstruction SQLite.

## Table auxiliaire de performance

`model_scorecard` est une table d’une ligne, sans relation, exportée pour permettre l’affichage Power BI des métriques calculées hors échantillon (ROC-AUC, PR-AUC, KS, précision, rappel, seuil et matrice de confusion). Elle n’est pas une dimension et ne change pas le schéma en étoile du portefeuille. Les colonnes et valeurs proviennent de `results/model_metrics.csv`.

`_Mesures` est une table de mesures créée dans Power BI Desktop; elle n’est pas importée depuis les CSV. Le nombre de mesures DAX est généré dans `qa/validation_report.md`.

## Contrat analytique

La cible est `default_next_month`. Le modèle est entraîné sur une partition stratifiée de 70 % et évalué sur une partition test de 30 %, avec `random_state=42`. Les prédicteurs numériques sont imputés par la médiane et standardisés; `education` est imputée par le mode puis encodée en indicatrices. `sex`, `marriage`, `age`, leurs valeurs source et `client_id` sont exclus du score. Ils restent disponibles uniquement pour les descriptifs permis.

Le score présent dans `fact_clients` est produit par un modèle ajusté sur la partition d’entraînement. Les statistiques de performance, de calibration, de lift, de bande de risque et de perte attendue doivent être filtrées sur `model_partition = "Test"`. Les scores de la partition Train sont des scores d’ajustement, pas une preuve de généralisation.

Les quatre bandes de score utilisent des seuils fixes documentés : Faible `<0,10`; Modéré `0,10–<0,20`; Élevé `0,20–<0,40`; Très élevé `≥0,40`. L’exposition de perte attendue est `max(0, bill_amt1)` en NT$; la LGD de base est une hypothèse de 45 %, avec analyse de sensibilité à 30 % et 60 %.

## Types utiles

Les identifiants et codes sont entiers; limites, soldes, paiements, ratios, PD et expositions sont numériques; libellés et partition sont textuels. Les CSV traités sont UTF-8. `payment_ratio_m1` est vide lorsque `bill_amt1 <= 0`; les autres champs bruts n’ont pas de valeur manquante à la lecture initiale. Les tables et leurs nombres de lignes sont générés dans `qa/validation_report.md`.
