# Contrôles qualité — Austin Budget vs Actual

| Contrôle | Résultat | Statut |
|---|---:|:---:|
| Lignes brutes | 57,267 | PASS |
| Lignes préparées | 57,267 | PASS |
| Colonnes préparées | 25 | PASS |
| Doublons de lignes | 0 | PASS |
| Clés uniques | 57,267 | PASS |
| Valeurs manquantes budget | 0 | PASS |
| Valeurs manquantes dépenses | 0 | PASS |
| Budgets égaux à zéro | 26,552 | PASS |
| Montants négatifs | 1,746 | PASS |

## Règles appliquées

- Les lignes originales sont conservées ; aucune ligne n’est supprimée automatiquement.
- `variance` = dépenses réelles − budget.
- Un écart positif est défavorable pour une dépense, car il signifie que la dépense réelle dépasse le budget.
- Le pourcentage d’écart n’est pas calculé lorsque le budget vaut zéro, afin d’éviter une division impossible.
- Les montants négatifs et les budgets nuls sont signalés pour analyse métier, pas corrigés silencieusement.
