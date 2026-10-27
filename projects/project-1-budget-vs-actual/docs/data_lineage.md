# Cheminement des données

## Étapes

| Étape | Entrée | Transformation | Sortie |
|---|---|---|---|
| 1. Source | Portail officiel City of Austin | Téléchargement API Socrata | `data/raw/austin_budget_vs_expense_full.csv` |
| 2. Contrôle initial | Fichier brut | Vérification des colonnes, lignes, valeurs vides et doublons | `checks/austin_full_profile.txt` |
| 3. Préparation | Fichier brut | Nettoyage des textes, conversion des codes en identifiants, calcul des écarts et alertes | `data/processed/austin_budget_vs_actual_prepared.csv` |
| 4. Agrégation | Fichier préparé | Regroupement par département ou catégorie | `data/processed/department_variance_summary.csv` et `expense_variance_summary.csv` |
| 5. Restitution | Synthèses calculées | Création de graphiques et de formules Power BI | `visuals/`, `dashboard/measures.dax` et fichier Excel |
| 6. Décision | Graphiques et indicateurs | Lecture des écarts et priorisation des vérifications | `reports/management_pack.md` |

## Principe de traçabilité

Chaque résultat doit pouvoir être relié à une ligne du fichier préparé, puis à une ligne du fichier brut. Les colonnes ajoutées par calcul sont séparées conceptuellement des colonnes directement téléchargées : `variance`, `variance_pct`, `budget_zero_flag`, `negative_amount_flag`, `unfavorable_flag` et `period_label` sont des colonnes calculées par le projet.
