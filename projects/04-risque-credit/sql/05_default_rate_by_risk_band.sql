SELECT
    d.risk_band_key,
    d.risk_band_label,
    COUNT(*) AS clients,
    SUM(f.default_next_month) AS defaults,
    AVG(CAST(f.default_next_month AS REAL)) AS default_rate,
    SUM(CASE WHEN f.bill_amt1 > 0 THEN f.bill_amt1 ELSE 0 END) AS positive_bill_exposure_ntd
FROM fact_clients AS f
JOIN dim_risk_band AS d ON d.risk_band_key = f.risk_band_key
WHERE f.model_partition = 'Test'
GROUP BY d.risk_band_key, d.risk_band_label
ORDER BY d.ordre;
