# Définitions des indicateurs

| Indicateur | Formule simple | Interprétation |
|---|---|---|
| Budget | Somme de la colonne `budget` | Montant prévu |
| Dépenses réelles | Somme de la colonne `expenditures` | Montant effectivement dépensé |
| Écart | Dépenses réelles − Budget | Positif = dépassement ; négatif = dépenses inférieures au budget |
| Écart % | Écart ÷ Budget | Mesure relative, uniquement si le budget est différent de zéro |
| Taux de consommation | Dépenses réelles ÷ Budget | Part du budget déjà utilisée |
| Lignes en dépassement | Nombre de lignes où l’écart est positif | Permet de voir les problèmes détaillés même si le total d’un département reste sous le budget |
| Budget nul | Nombre de lignes où le budget vaut zéro | Cas à examiner séparément, car le pourcentage n’est pas calculable |
| Montant négatif | Ligne où le budget ou les dépenses sont négatifs | Peut correspondre à une correction, une annulation ou un remboursement |

## Règle importante

L’écart est calculé comme `dépenses réelles − budget`. Cette convention est choisie parce que le projet analyse des **dépenses**. Pour une dépense, un résultat positif est défavorable : l’organisation a dépensé plus que prévu.
