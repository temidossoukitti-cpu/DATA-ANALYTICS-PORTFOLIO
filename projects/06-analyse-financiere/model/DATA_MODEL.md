# Modèle de données Power BI

## Tables chargées

| Table | Rôle | Clé / volume attendu |
|---|---|---|
| `dim_fiscal_year` | Dimension des exercices annuels | `fiscal_year_key`, sept lignes (2019–2025) |
| `dim_metric` | Dictionnaire des quinze indicateurs comptables | `metric_key`, quinze lignes |
| `dim_ratio` | Dictionnaire des dix-neuf ratios calculés | `ratio_key`, dix-neuf lignes |
| `fact_financials` | Valeurs comptables annuelles | `(fiscal_year_key, metric_key)`, 105 lignes |
| `fact_ratios` | Ratios annuels calculés | `(fiscal_year_key, ratio_key)`, 130 lignes |
| `financial_scorecard` | Fiche de synthèse du dernier exercice | une ligne |
| `financial_alerts` | Seuils de lecture et statut observé | six lignes |

Les volumes sont régénérés par le pipeline; ils ne signifient pas qu’un dashboard a déjà été construit.

## Clés et relations

Créer ces relations actives à sens unique, depuis les dimensions vers les faits :

- `dim_fiscal_year[fiscal_year_key]` 1 → * `fact_financials[fiscal_year_key]` et 1 → * `fact_ratios[fiscal_year_key]`.
- `dim_metric[metric_key]` 1 → * `fact_financials[metric_key]`.
- `dim_ratio[ratio_key]` 1 → * `fact_ratios[ratio_key]`.

`financial_scorecard` et `financial_alerts` sont des tables de synthèse déconnectées; ne pas créer de relation ambiguë. Utiliser `financial_scorecard` pour les cartes du dernier exercice et `financial_alerts` pour la page de pilotage.

## Unités et interprétation

Les montants de `fact_financials` sont exprimés en **dollars américains**, sans arrondi intermédiaire. Le BPA dilué est en **dollars par action**; les actions diluées sont en **millions**. Les ratios sont sans unité, sauf mention contraire dans `dim_ratio[unit]`. Ne pas ajouter de symbole monétaire aux ratios.

`fiscal_year_key` est l’année civile de clôture (31 décembre). Les comparaisons annuelles portent sur des exercices complets; aucun cumul infra-annuel n’existe dans la source. La croissance de la première année est absente par construction (pas d’exercice précédent dans la fenêtre).

Les valeurs de `financial_scorecard` correspondent à l’exercice le plus récent; elles ne se recalculent pas à partir de filtres de page. Pour les cartes sensibles à la sélection, utiliser les mesures DAX sur `fact_financials` et `fact_ratios`.
