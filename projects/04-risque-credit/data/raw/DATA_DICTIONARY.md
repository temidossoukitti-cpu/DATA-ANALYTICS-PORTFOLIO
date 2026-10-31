# Dictionnaire des données

## Fichier et conventions

Le classeur XLS original contient 30 000 lignes et 25 colonnes. La première ligne porte les identifiants génériques X1–X23; la deuxième est l’en-tête métier lue par `header=1`. Les montants sont en nouveau dollar taïwanais (NT$). La période d’observation des historiques de paiement est d’avril à septembre 2005. Les noms français et anglais utilisent `snake_case` dans les fichiers traités.

| # | Nom source | Nom traité | Définition et valeurs |
|---:|---|---|---|
| 1 | `ID` | `client_id` | Identifiant séquentiel du client; clé technique, jamais prédicteur. |
| 2 | `LIMIT_BAL` | `limit_bal` | Montant de la limite de crédit accordée au client et à sa famille, en NT$. |
| 3 | `SEX` | `sex` | Sexe tel que codé dans la source : 1 = homme; 2 = femme. Descriptif uniquement. |
| 4 | `EDUCATION` | `education` | Niveau : 1 = graduate school; 2 = université; 3 = lycée; 4 = autres. Les codes 0, 5 et 6 sont recodés en 4; `education_original` conserve la valeur source. |
| 5 | `MARRIAGE` | `marriage` | État matrimonial : 1 = marié; 2 = célibataire; 3 = autre. Le code 0 est recodé en 3; `marriage_original` conserve la valeur source. Descriptif uniquement. |
| 6 | `AGE` | `age` | Âge en années; descriptif uniquement dans ce projet. |
| 7 | `PAY_0` | `pay_0` | Statut de remboursement le plus récent : septembre 2005. |
| 8 | `PAY_2` | `pay_2` | Statut de remboursement d’août 2005. |
| 9 | `PAY_3` | `pay_3` | Statut de remboursement de juillet 2005. |
| 10 | `PAY_4` | `pay_4` | Statut de remboursement de juin 2005. |
| 11 | `PAY_5` | `pay_5` | Statut de remboursement de mai 2005. |
| 12 | `PAY_6` | `pay_6` | Statut de remboursement d’avril 2005. |
| 13 | `BILL_AMT1` | `bill_amt1` | Montant du relevé de septembre 2005, en NT$. |
| 14 | `BILL_AMT2` | `bill_amt2` | Montant du relevé d’août 2005, en NT$. |
| 15 | `BILL_AMT3` | `bill_amt3` | Montant du relevé de juillet 2005, en NT$. |
| 16 | `BILL_AMT4` | `bill_amt4` | Montant du relevé de juin 2005, en NT$. |
| 17 | `BILL_AMT5` | `bill_amt5` | Montant du relevé de mai 2005, en NT$. |
| 18 | `BILL_AMT6` | `bill_amt6` | Montant du relevé d’avril 2005, en NT$. |
| 19 | `PAY_AMT1` | `pay_amt1` | Montant payé en septembre 2005, en NT$. |
| 20 | `PAY_AMT2` | `pay_amt2` | Montant payé en août 2005, en NT$. |
| 21 | `PAY_AMT3` | `pay_amt3` | Montant payé en juillet 2005, en NT$. |
| 22 | `PAY_AMT4` | `pay_amt4` | Montant payé en juin 2005, en NT$. |
| 23 | `PAY_AMT5` | `pay_amt5` | Montant payé en mai 2005, en NT$. |
| 24 | `PAY_AMT6` | `pay_amt6` | Montant payé en avril 2005, en NT$. |
| 25 | `default payment next month` | `default_next_month` | Cible binaire : 1 = défaut le mois suivant; 0 = pas de défaut. |

**Aucune colonne `PAY_1` n’existe dans le fichier original.** Elle n’est ni reconstruite ni imputée.

## Codes de remboursement

La documentation UCI définit `-1` comme paiement à jour et `1` à `9` comme retard de un à neuf mois ou davantage. Dans ce projet, les codes `-2` (« aucun achat déclaré ») et `0` (« crédit renouvelable ») suivent les hypothèses métier fournies avec les consignes; ils ne sont pas présentés comme des définitions vérifiées par UCI. Aucun client n’est supprimé pour ces codes.

## Recodages conservant la source

`education_original` et `marriage_original` gardent les valeurs brutes. La variable analysée `education` transforme 0, 5 et 6 en 4 (« autre/inconnu »). La variable analysée `marriage` transforme 0 en 3 (« autre »). Les effectifs de chaque recodage sont générés dans `results/quality_check.csv`.

## Variables dérivées

- `age_band` : `<25`, `25–34`, `35–44`, `45–54`, `55+`.
- `limit_band` : quintiles de `limit_bal`, calculés sur le fichier source; les bornes et les libellés figurent dans `dim_limit_band.csv`.
- `utilization_raw` : `bill_amt1 / limit_bal`. `utilization` est plafonnée à l’intervalle 0–1,5 : les utilisations négatives sont ramenées à 0 et celles au-dessus de 150 % sont plafonnées à 150 %. Ces bornes sont des hypothèses de préparation, pas des seuils réglementaires.
- `payment_ratio_m1` : `pay_amt1 / bill_amt1` seulement lorsque `bill_amt1 > 0`; sinon la valeur est manquante. Aucun plafonnement supplémentaire n’est appliqué.
- `max_delay_6m` : retard mensuel maximum parmi `pay_0`, `pay_2` à `pay_6`, en ne retenant que les codes positifs; 0 signifie qu’aucun code positif n’est observé.
- `n_delays_6m` : nombre de statuts mensuels positifs parmi les six périodes.
- `risk_flag_recent_delay` : 1 lorsque `pay_0 >= 1`, sinon 0.
- `utilization_band` : `<30 %`, `30–<60 %`, `60–100 %`, `>100 %`; regroupement descriptif.

La cible est déséquilibrée. L’analyse rapporte précision, rappel, AUC ROC et PR-AUC plutôt que de s’appuyer sur l’accuracy seule.
