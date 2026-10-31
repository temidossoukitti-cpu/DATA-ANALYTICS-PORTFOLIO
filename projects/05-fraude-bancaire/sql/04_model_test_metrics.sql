-- Métriques de classification pondérées; la partition contient uniquement des scores hors échantillon.
WITH counts AS (
    SELECT
        SUM(CASE WHEN o.is_fraud = 1 AND f.model_prediction = 1 THEN f.eval_population_weight ELSE 0 END) AS tp,
        SUM(CASE WHEN o.is_fraud = 0 AND f.model_prediction = 1 THEN f.eval_population_weight ELSE 0 END) AS fp,
        SUM(CASE WHEN o.is_fraud = 1 AND f.model_prediction = 0 THEN f.eval_population_weight ELSE 0 END) AS fn,
        SUM(f.eval_population_weight) AS transactions_estimate
    FROM fact_model_test AS f
    JOIN dim_outcome AS o ON o.outcome_key = f.outcome_key
)
SELECT
    transactions_estimate,
    tp AS fraud_transactions_intercepted_estimate,
    fp AS legitimate_transactions_flagged_estimate,
    fn AS fraud_transactions_missed_estimate,
    1.0 * tp / NULLIF(tp + fp, 0) AS precision_weighted,
    1.0 * tp / NULLIF(tp + fn, 0) AS recall_weighted
FROM counts;
