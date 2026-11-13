# Modèle de données — Global Findex

La table source est une table large d’estimations d’enquête. Une ligne correspond à une économie, une année et une dimension de sous-groupe. `group=all` et `group2=all` représentent la vue nationale générale. Les autres groupes couvrent notamment `gender`, `income`, `age_cat`, `urbanicity`, `laborforce` et `education`.

Les indicateurs du dashboard sont conservés dans `data/processed/country_indicators.csv` et documentés dans `data/processed/indicator_dictionary.csv`.

| Champ source | Libellé dashboard |
|---|---|
| `account_t_d` | Compte ou mobile money |
| `fiaccount_t_d` | Compte bancaire / institution financière |
| `mobileaccount_t_d` | Compte mobile money |
| `fin26a` | Paiement de factures en ligne |
| `fin26b` | Achat en ligne |
| `save_any_t_d` | Épargne |
| `borrow_any_t_d` | Emprunt |
| `con1` | Possession d’un téléphone mobile |
| `internet` | Usage récent d’internet |

Les agrégations pondérées utilisent `pop_adult`. Aucun taux n’est imputé lorsqu’une valeur source est absente.
