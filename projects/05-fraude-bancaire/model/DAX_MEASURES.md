# Mesures DAX

Créer une table dédiée `_Mesures` dans Power BI Desktop et y placer ces définitions. Les noms sont en français et sans unité intégrée; choisir ensuite les formats de pourcentage ou de nombre dans Desktop. Chaque expression est commentée et classée dans un dossier d’affichage.

### M01 · Transactions estimées
```DAX
// Total estimé à partir du plan d'échantillonnage stratifié.
Transactions estimées = SUM(fact_transactions[sampling_weight])
```
Dossier d’affichage : `01 Population`.

### M02 · Fraudes estimées
```DAX
// Nombre estimé de transactions Class=1.
Fraudes estimées = CALCULATE([Transactions estimées], dim_outcome[is_fraud] = 1)
```
Dossier d’affichage : `01 Population`.

### M03 · Taux de fraude pondéré
```DAX
// Fraudes estimées divisées par les transactions estimées.
Taux de fraude pondéré = DIVIDE([Fraudes estimées], [Transactions estimées])
```
Dossier d’affichage : `01 Population`.

### M04 · Montant estimé
```DAX
// Somme de Amount pondérée; unité monétaire non fournie par la source.
Montant estimé = SUMX(fact_transactions, fact_transactions[amount] * fact_transactions[sampling_weight])
```
Dossier d’affichage : `02 Exposition`.

### M05 · Exposition fraude estimée
```DAX
// Amount pondéré sur les lignes étiquetées fraude.
Exposition fraude estimée = CALCULATE([Montant estimé], dim_outcome[is_fraud] = 1)
```
Dossier d’affichage : `02 Exposition`.

### M06 · Transactions test estimées
```DAX
// La partition test est recalibrée par classe sur les effectifs source connus.
Transactions test estimées = SUM(fact_model_test[eval_population_weight])
```
Dossier d’affichage : `03 Modèle`.

### M07 · Transactions signalées par le modèle
```DAX
// Volume estimé de décisions positives au seuil documenté.
Transactions signalées modèle = SUMX(fact_model_test, fact_model_test[eval_population_weight] * fact_model_test[model_prediction])
```
Dossier d’affichage : `03 Modèle`.

### M08 · Précision test pondérée
```DAX
// TP pondérés / toutes les alertes positives pondérées.
Précision test pondérée =
DIVIDE(
    SUMX(fact_model_test, fact_model_test[eval_population_weight] * fact_model_test[model_prediction] * fact_model_test[outcome_key]),
    [Transactions signalées modèle]
)
```
Dossier d’affichage : `03 Modèle`.

### M09 · Rappel test pondéré
```DAX
// TP pondérés / fraudes test pondérées.
Rappel test pondéré =
DIVIDE(
    SUMX(fact_model_test, fact_model_test[eval_population_weight] * fact_model_test[model_prediction] * fact_model_test[outcome_key]),
    SUMX(fact_model_test, fact_model_test[eval_population_weight] * fact_model_test[outcome_key])
)
```
Dossier d’affichage : `03 Modèle`.

### M10 · F1 test pondéré
```DAX
// Moyenne harmonique de précision et rappel pondérés.
F1 test pondéré = DIVIDE(2 * [Précision test pondérée] * [Rappel test pondéré], [Précision test pondérée] + [Rappel test pondéré])
```
Dossier d’affichage : `03 Modèle`.

### M11 · PR-AUC test
```DAX
// Average precision pondérée issue de la partition test.
PR-AUC test = MAX(model_scorecard[pr_auc_test])
```
Dossier d’affichage : `03 Modèle`.

### M12 · Seuil recommandé
```DAX
// Seuil coût-minimal sélectionné sur les prédictions hors pli du train.
Seuil recommandé = MAX(model_scorecard[recommended_threshold])
```
Dossier d’affichage : `03 Modèle`.

### M13 · Exposition fraude interceptée
```DAX
// Somme de Amount pondérée des fraudes signalées sur le test.
Exposition fraude interceptée = SUM(fact_model_test[fraud_amount_intercepted_contribution])
```
Dossier d’affichage : `04 Décision et coût`.

### M14 · Exposition fraude manquée
```DAX
// Somme de Amount pondérée des fraudes non signalées sur le test.
Exposition fraude manquée = SUM(fact_model_test[fraud_amount_missed_contribution])
```
Dossier d’affichage : `04 Décision et coût`.

### M15 · Coût prévu du modèle
```DAX
// Coût selon les hypothèses de perte manquée et friction légitime stockées ligne à ligne.
Coût prévu modèle = SUM(fact_model_test[expected_cost_contribution])
```
Dossier d’affichage : `04 Décision et coût`.

<!-- AUTO:DAX_EXPECTED_BEGIN -->
| ID | Mesure | Valeur attendue depuis les sorties générées |
|---|---|---|
| M01 | Transactions estimées | 284 807 |
| M02 | Fraudes estimées | 492 |
| M03 | Taux de fraude pondéré | 0,173 % |
| M04 | Montant estimé | 24 469 924,29 unités du dataset |
| M05 | Exposition fraude estimée | 60 127,97 unités du dataset |
| M06 | Transactions test estimées | 284 807 |
| M07 | Transactions signalées modèle | 591,79 |
| M08 | Précision test pondérée | 67,97 % |
| M09 | Rappel test pondéré | 81,76 % |
| M10 | F1 test pondéré | 74,23 % |
| M11 | PR-AUC test | 0.6595 |
| M12 | Seuil recommandé | 0.191 |
| M13 | Exposition fraude interceptée | 44 976,15 unités du dataset |
| M14 | Exposition fraude manquée | 12 293,15 unités du dataset |
| M15 | Coût prévu modèle | 14 188,59 unités du dataset |
<!-- AUTO:DAX_EXPECTED_END -->
