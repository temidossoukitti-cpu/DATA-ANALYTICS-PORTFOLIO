# Mesures DAX

Créer dans Power BI Desktop une table dédiée `_Mesures` avec `ROW("Ancre", 1)`, puis ajouter les mesures ci-dessous. Renseigner leur propriété **Dossier d’affichage** selon la colonne indiquée. Les nombres de mesures sont générés dans `qa/validation_report.md`.

Créer aussi la table déconnectée `Param_LGD` avec `GENERATESERIES(0.30, 0.60, 0.15)`. La valeur par défaut de la mesure de perte attendue est 45 %; cette LGD reste une hypothèse et le sélecteur permet d’examiner la sensibilité.

```DAX
_Mesures = ROW("Ancre", 1)
Param_LGD = GENERATESERIES(0.30, 0.60, 0.15)
```

Les valeurs attendues ci-dessous proviennent des CSV `results/` générés par le pipeline. Les mesures de score et de perte attendue concernent la partition test; les mesures de portefeuille s’appliquent au contexte de filtre courant.

### 01 · Nombre de clients

**Dossier d’affichage :** `Portefeuille`. **Commentaire :** Compte les clients distincts dans le contexte de filtre. **Valeur attendue :** 30 000.

```DAX
Nombre de clients = DISTINCTCOUNT(fact_clients[client_id])
```

### 02 · Taux de défaut

**Dossier d’affichage :** `Défauts`. **Commentaire :** Défauts du mois suivant divisés par les clients dans le contexte. **Valeur attendue :** 22,12 %.

```DAX
Taux de défaut = DIVIDE(SUM(fact_clients[default_next_month]), [Nombre de clients])
```

### 03 · Limite de crédit totale

**Dossier d’affichage :** `Portefeuille`. **Commentaire :** Somme des limites autorisées, en NT$. **Valeur attendue :** NT$ 5 024 529 680.

```DAX
Limite de crédit totale = SUM(fact_clients[limit_bal])
```

### 04 · Limite moyenne

**Dossier d’affichage :** `Portefeuille`. **Commentaire :** Limite moyenne accordée, en NT$. **Valeur attendue :** NT$ 167 484.

```DAX
Limite moyenne = AVERAGE(fact_clients[limit_bal])
```

### 05 · Exposition des défaillants

**Dossier d’affichage :** `Exposition`. **Commentaire :** Somme des limites des clients ayant fait défaut le mois suivant, en NT$. **Valeur attendue :** NT$ 863 407 680.

```DAX
Exposition des défaillants = CALCULATE(SUM(fact_clients[limit_bal]), fact_clients[default_next_month] = 1)
```

### 06 · Part de l’exposition des défaillants

**Dossier d’affichage :** `Exposition`. **Commentaire :** Exposition des défaillants divisée par la limite totale. **Valeur attendue :** 17,18 %.

```DAX
Part de l’exposition des défaillants = DIVIDE([Exposition des défaillants], [Limite de crédit totale])
```

### 07 · Utilisation moyenne

**Dossier d’affichage :** `Utilisation`. **Commentaire :** Moyenne de l’utilisation plafonnée à 150 % selon l’hypothèse documentée. **Valeur attendue :** 42,12 %.

```DAX
Utilisation moyenne = AVERAGE(fact_clients[utilization])
```

### 08 · Part des clients à risque élevé

**Dossier d’affichage :** `Risque`. **Commentaire :** Part des clients de la partition test dans les bandes Élevé et Très élevé. **Valeur attendue :** 31,89 %.

```DAX
Part des clients à risque élevé = VAR TestClients = CALCULATE(DISTINCTCOUNT(fact_clients[client_id]), fact_clients[model_partition] = "Test")
VAR HighRiskClients = CALCULATE(DISTINCTCOUNT(fact_clients[client_id]), fact_clients[model_partition] = "Test", fact_clients[risk_band_key] >= 3)
RETURN DIVIDE(HighRiskClients, TestClients)
```

### 09 · ROC-AUC test

**Dossier d’affichage :** `Modèle`. **Commentaire :** Aire ROC issue de la partition test stratifiée. **Valeur attendue :** 0,7536.

```DAX
ROC-AUC test = MAX(model_scorecard[roc_auc])
```

### 10 · PR-AUC test

**Dossier d’affichage :** `Modèle`. **Commentaire :** Average precision (aire précision-rappel) sur la partition test. **Valeur attendue :** 0,5016.

```DAX
PR-AUC test = MAX(model_scorecard[pr_auc_average_precision])
```

### 11 · KS test

**Dossier d’affichage :** `Modèle`. **Commentaire :** Écart maximal entre les distributions cumulées des deux classes. **Valeur attendue :** 0,3948.

```DAX
KS test = MAX(model_scorecard[ks_statistic])
```

### 12 · Précision au seuil

**Dossier d’affichage :** `Modèle`. **Commentaire :** Précision calculée au seuil de classification documenté. **Valeur attendue :** 45,32 %.

```DAX
Précision au seuil = MAX(model_scorecard[precision_at_threshold])
```

### 13 · Rappel au seuil

**Dossier d’affichage :** `Modèle`. **Commentaire :** Rappel calculé au seuil de classification documenté. **Valeur attendue :** 58,81 %.

```DAX
Rappel au seuil = MAX(model_scorecard[recall_at_threshold])
```

### 14 · Perte attendue

**Dossier d’affichage :** `Pertes`. **Commentaire :** Somme de PD × facture positive × LGD paramétrée, filtrée sur la partition test. **Valeur attendue :** NT$ 43 390 137.

```DAX
Perte attendue = VAR LGD = SELECTEDVALUE(Param_LGD[Value], 0.45)
RETURN CALCULATE(SUMX(fact_clients, fact_clients[predicted_pd] * IF(fact_clients[bill_amt1] > 0, fact_clients[bill_amt1], 0) * LGD), fact_clients[model_partition] = "Test")
```
