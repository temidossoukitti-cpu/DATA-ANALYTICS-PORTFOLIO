-- Indicateur global pondéré sur l'échantillon de transactions.
SELECT
    SUM(f.sampling_weight) AS transactions_estimate,
    SUM(CASE WHEN o.is_fraud = 1 THEN f.sampling_weight ELSE 0 END) AS fraud_transactions_estimate,
    SUM(f.sampling_weight * f.amount) AS amount_estimate,
    SUM(CASE WHEN o.is_fraud = 1 THEN f.sampling_weight * f.amount ELSE 0 END) AS fraud_amount_estimate,
    1.0 * SUM(CASE WHEN o.is_fraud = 1 THEN f.sampling_weight ELSE 0 END)
        / NULLIF(SUM(f.sampling_weight), 0) AS fraud_rate
FROM fact_transactions AS f
JOIN dim_outcome AS o ON o.outcome_key = f.outcome_key;
