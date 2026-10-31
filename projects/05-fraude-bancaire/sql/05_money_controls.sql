-- Montants d'exposition estimés et coût selon les hypothèses explicitement documentées.
WITH strategies AS (
    SELECT 'Modèle logistique' AS method, f.*, f.model_prediction AS flagged FROM fact_model_test AS f
    UNION ALL
    SELECT 'Règle montant P99' AS method, f.*, f.baseline_amount_flag AS flagged FROM fact_model_test AS f
)
SELECT
    s.method,
    SUM(CASE WHEN s.flagged = 1 THEN s.eval_population_weight ELSE 0 END) AS transactions_flagged_estimate,
    SUM(CASE WHEN o.is_fraud = 1 AND s.flagged = 1 THEN s.eval_population_weight ELSE 0 END) AS fraud_transactions_intercepted_estimate,
    SUM(CASE WHEN o.is_fraud = 1 AND s.flagged = 0 THEN s.eval_population_weight ELSE 0 END) AS fraud_transactions_missed_estimate,
    SUM(CASE WHEN o.is_fraud = 0 AND s.flagged = 1 THEN s.eval_population_weight ELSE 0 END) AS legitimate_transactions_blocked_estimate,
    SUM(CASE WHEN s.flagged = 1 THEN s.eval_population_weight * s.amount ELSE 0 END) AS amount_flagged_estimate,
    SUM(CASE WHEN o.is_fraud = 1 AND s.flagged = 1 THEN s.eval_population_weight * s.amount ELSE 0 END) AS fraud_amount_intercepted_estimate,
    SUM(CASE WHEN o.is_fraud = 1 AND s.flagged = 0 THEN s.eval_population_weight * s.amount ELSE 0 END) AS fraud_amount_missed_estimate,
    SUM(CASE WHEN o.is_fraud = 0 AND s.flagged = 1 THEN s.eval_population_weight * s.amount ELSE 0 END) AS legitimate_amount_blocked_estimate,
    SUM(CASE
        WHEN o.is_fraud = 1 AND s.flagged = 0 THEN s.eval_population_weight * s.amount * s.loss_severity_assumption
        WHEN o.is_fraud = 0 AND s.flagged = 1 THEN s.eval_population_weight * s.legitimate_friction_cost_assumption
        ELSE 0 END) AS expected_cost_estimate
FROM strategies AS s
JOIN dim_outcome AS o ON o.outcome_key = s.outcome_key
GROUP BY s.method
ORDER BY s.method;
