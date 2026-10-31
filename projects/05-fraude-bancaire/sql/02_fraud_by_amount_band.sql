-- Taux, effectifs estimés et exposition par bande; les unités de montant ne sont pas une devise.
SELECT
    b.amount_band_key,
    b.label_fr,
    SUM(f.sampling_weight) AS transactions_estimate,
    SUM(CASE WHEN o.is_fraud = 1 THEN f.sampling_weight ELSE 0 END) AS fraud_transactions_estimate,
    1.0 * SUM(CASE WHEN o.is_fraud = 1 THEN f.sampling_weight ELSE 0 END)
        / NULLIF(SUM(f.sampling_weight), 0) AS fraud_rate,
    SUM(f.sampling_weight * f.amount) AS amount_estimate,
    SUM(CASE WHEN o.is_fraud = 1 THEN f.sampling_weight * f.amount ELSE 0 END) AS fraud_amount_estimate
FROM fact_transactions AS f
JOIN dim_outcome AS o ON o.outcome_key = f.outcome_key
JOIN dim_amount_band AS b ON b.amount_band_key = f.amount_band_key
GROUP BY b.amount_band_key, b.label_fr, b.sort_order
ORDER BY b.sort_order;
