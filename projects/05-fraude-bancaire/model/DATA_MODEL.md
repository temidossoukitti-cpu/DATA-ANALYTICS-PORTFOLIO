# Modèle de données Power BI

## Tables chargées

| Table | Rôle | Clé / volume attendu |
|---|---|---|
| `dim_outcome` | Dimension du résultat, 0 légitime / 1 fraude | `outcome_key`, deux lignes |
| `dim_amount_band` | Bandes descriptives de montant | `amount_band_key`, quatre lignes |
| `dim_time_window` | Fenêtres relatives de six heures | `time_window_key`, huit lignes |
| `fact_transactions` | Fait de base de l’échantillon pondéré | `transaction_id`, 25 492 lignes |
| `fact_model_test` | Scores et décisions sur la seule partition test | `transaction_id`, 7 648 lignes, sous-ensemble de `fact_transactions` |
| `model_scorecard` | KPI agrégés du modèle retenu | une ligne |
| `model_cost_sensitivity` | Seuil et coût sous neuf hypothèses | neuf lignes |
| `model_money_controls` | Comparaison modèle / règle P99 | deux lignes |

Les nombres ci-dessus sont régénérés par `qa/validation_report.md`; ils ne signifient pas qu’un dashboard a déjà été construit.

## Clés et relations

Créer ces relations actives à sens unique, depuis la dimension vers les faits :

- `dim_outcome[outcome_key]` 1 → * `fact_transactions[outcome_key]` et 1 → * `fact_model_test[outcome_key]`.
- `dim_amount_band[amount_band_key]` 1 → * les deux tables de faits par leurs clés de bande.
- `dim_time_window[time_window_key]` 1 → * les deux tables de faits par leurs clés temporelles.
- `fact_transactions[transaction_id]` 1 → 0..1 `fact_model_test[transaction_id]`; chaque score test appartient à une ligne de l’échantillon.

`model_scorecard`, `model_cost_sensitivity` et `model_money_controls` sont des tables de synthèse déconnectées; ne pas créer de relation ambiguë. Utiliser `model_scorecard` pour les cartes de performance et `model_cost_sensitivity` pour la matrice d’hypothèses.

## Poids et interprétation

`sampling_weight` sert à estimer les effectifs et sommes de la population à partir de l’échantillon stratifié; ce n’est jamais une variable explicative. Toutes les fraudes du fichier source sont conservées; chaque fraude a un poids 1 et chaque légitime échantillonnée un poids 11.3726.

`eval_population_weight` est recalibré par classe sur la partition test pour que les totaux pondérés de classe correspondent aux effectifs source connus. Le test garde 7 648 lignes brutes, même si ses poids représentent la population entière. Les KPI pondérés décrivent une estimation de cette population, pas de nouvelles observations indépendantes.

`transaction_id` est un numéro de ligne technique; ce n’est pas un identifiant bancaire. `Time` devient `time_seconds` et ses filtres sont relatifs à la première transaction. Aucune dimension date, client, marchand, type de transaction ou devise n’existe. Les montants ne doivent pas être formatés en monnaie sans information externe validée.
