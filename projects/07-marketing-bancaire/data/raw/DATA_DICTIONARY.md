# Dictionnaire des données

La source contient 20 variables explicatives et la cible `y`. Les valeurs `unknown` sont des modalités explicites de la source et ne sont pas imputées.

| Groupe | Variables | Rôle |
|---|---|---|
| Client | `age`, `job`, `marital`, `education`, `default`, `housing`, `loan` | Profil descriptif et situation de crédit déclarée |
| Campagne | `contact`, `month`, `day_of_week`, `campaign`, `pdays`, `previous`, `poutcome` | Historique et contexte des contacts |
| Macroéconomie | `emp.var.rate`, `cons.price.idx`, `cons.conf.idx`, `euribor3m`, `nr.employed` | Conditions économiques au moment de la campagne |
| Appel | `duration` | Durée du dernier appel ; exclue du modèle prospectif |
| Cible | `y` | Souscription d'un dépôt à terme : `yes` ou `no` |

## Champs dérivés

`campaign_id` identifie la ligne de campagne. `outcome_key` encode la cible en 0/1. Les dimensions `dim_*` portent les libellés français et les ordres d'affichage. `age_band_key` regroupe l'âge en six classes et `campaign_band_key` regroupe le nombre de contacts. `previously_contacted` indique si `pdays` est différent de 999.

Les tables Power BI préparées sont `fact_campaign`, `dim_outcome`, `dim_job`, `dim_education`, `dim_marital`, `dim_month`, `dim_contact`, `dim_poutcome`, `dim_age_band` et `dim_campaign_band`.
