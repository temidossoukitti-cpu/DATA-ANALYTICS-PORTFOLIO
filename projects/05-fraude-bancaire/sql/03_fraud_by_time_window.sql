-- Fenêtres relatives de six heures depuis le premier enregistrement; ce ne sont pas des heures civiles.
SELECT
    d.time_window_key,
    d.label_fr,
    SUM(f.sampling_weight) AS transactions_estimate,
    SUM(CASE WHEN o.is_fraud = 1 THEN f.sampling_weight ELSE 0 END) AS fraud_transactions_estimate,
    1.0 * SUM(CASE WHEN o.is_fraud = 1 THEN f.sampling_weight ELSE 0 END)
        / NULLIF(SUM(f.sampling_weight), 0) AS fraud_rate,
    SUM(f.sampling_weight * f.amount) AS amount_estimate,
    SUM(CASE WHEN o.is_fraud = 1 THEN f.sampling_weight * f.amount ELSE 0 END) AS fraud_amount_estimate
FROM fact_transactions AS f
JOIN dim_outcome AS o ON o.outcome_key = f.outcome_key
JOIN dim_time_window AS d ON d.time_window_key = f.time_window_key
GROUP BY d.time_window_key, d.label_fr, d.sort_order
ORDER BY d.sort_order;
