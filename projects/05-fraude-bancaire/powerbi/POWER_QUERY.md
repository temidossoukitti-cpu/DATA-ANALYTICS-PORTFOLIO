# Power Query — chargement des tables

Créer dans Power BI Desktop un paramètre texte nommé `DataFolder`. Sa valeur est le dossier `data/processed` de cette copie du dépôt; ne pas inscrire de chemin de poste dans le code M. Le dossier doit être configuré sans séparateur final. Les exports de modèle et de coûts sont déjà des CSV générés par le pipeline.

Créer une requête fonction `LoadCsv` :

```powerquery
(fileName as text) as table =>
let
    Source = Csv.Document(
        File.Contents(DataFolder & "/" & fileName),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true])
in
    Promoted
```

Créer les huit requêtes ci-dessous; les types sont explicites pour éviter les conversions automatiques ambiguës.

```powerquery
// dim_outcome
let
    Source = LoadCsv("dim_outcome.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"outcome_key", Int64.Type}, {"label_fr", type text}, {"is_fraud", Int64.Type}})
in Typed
```

```powerquery
// dim_amount_band
let
    Source = LoadCsv("dim_amount_band.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"amount_band_key", Int64.Type}, {"label_fr", type text}, {"lower_exclusive", type number}, {"upper_inclusive", type number}, {"sort_order", Int64.Type}})
in Typed
```

```powerquery
// dim_time_window
let
    Source = LoadCsv("dim_time_window.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"time_window_key", Int64.Type}, {"label_fr", type text}, {"start_second", Int64.Type}, {"end_second_exclusive", Int64.Type}, {"sort_order", Int64.Type}})
in Typed
```

```powerquery
// fact_transactions
let
    Source = LoadCsv("fact_transactions.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"transaction_id", Int64.Type}, {"time_seconds", type number}, {"amount", type number}, {"outcome_key", Int64.Type}, {"amount_band_key", Int64.Type}, {"time_window_key", Int64.Type}, {"sampling_weight", type number}, {"sample_partition", type text}})
in Typed
```

```powerquery
// fact_model_test
let
    Source = LoadCsv("fact_model_test.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"transaction_id", Int64.Type}, {"time_seconds", type number}, {"amount", type number}, {"outcome_key", Int64.Type}, {"sampling_weight", type number}, {"model_probability", type number}, {"model_prediction", Int64.Type}, {"baseline_amount_flag", Int64.Type}, {"eval_population_weight", type number}, {"loss_severity_assumption", type number}, {"legitimate_friction_cost_assumption", type number}, {"expected_cost_contribution", type number}, {"fraud_amount_missed_contribution", type number}, {"fraud_amount_intercepted_contribution", type number}, {"legitimate_amount_blocked_contribution", type number}, {"amount_band_key", Int64.Type}, {"time_window_key", Int64.Type}})
in Typed
```

```powerquery
// model_scorecard
let
    Source = LoadCsv("model_scorecard.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"model_name", type text}, {"recommended_threshold", type number}, {"pr_auc_test", type number}, {"precision_test", type number}, {"recall_test", type number}, {"f1_test", type number}, {"expected_cost_test", type number}, {"test_transactions_population_estimate", type number}, {"split_method", type text}, {"features_used", type text}})
in Typed
```

```powerquery
// model_cost_sensitivity
let
    Source = LoadCsv("model_cost_sensitivity.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"loss_severity_assumption", type number}, {"legitimate_friction_cost_assumption", type number}, {"threshold_selected_on_training_oof", type number}, {"test_expected_cost_estimate", type number}, {"test_weighted_precision", type number}, {"test_weighted_recall", type number}, {"test_fraud_amount_missed_estimate", type number}, {"test_legitimate_transactions_blocked_estimate", type number}, {"cost_unit", type text}})
in Typed
```

```powerquery
// model_money_controls
let
    Source = LoadCsv("model_money_controls.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"method", type text}, {"transactions_flagged_estimate", type number}, {"legitimate_transactions_blocked_estimate", type number}, {"fraud_transactions_intercepted_estimate", type number}, {"fraud_transactions_missed_estimate", type number}, {"amount_flagged_estimate", type number}, {"fraud_amount_intercepted_estimate", type number}, {"fraud_amount_missed_estimate", type number}, {"legitimate_amount_blocked_estimate", type number}, {"expected_cost_estimate", type number}, {"missed_fraud_loss_severity_assumption", type number}, {"legitimate_friction_cost_assumption", type number}, {"cost_unit", type text}})
in Typed
```

Après chargement, créer dans Power BI les relations indiquées dans `model/DATA_MODEL.md`, trier `label_fr` de `dim_time_window` par `sort_order` et désactiver le filtre bidirectionnel. `Time` n’étant pas une date civile, aucun calendrier n’est à créer.
