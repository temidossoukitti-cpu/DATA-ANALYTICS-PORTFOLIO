SELECT
    d.age_band_key,
    d.age_band_label,
    COUNT(*) AS clients,
    SUM(f.default_next_month) AS defaults,
    AVG(CAST(f.default_next_month AS REAL)) AS default_rate,
    SUM(CASE WHEN f.default_next_month = 1 THEN f.limit_bal ELSE 0 END) AS defaulter_credit_limit_exposure_ntd
FROM fact_clients AS f
JOIN dim_age_band AS d ON d.age_band_key = f.age_band_key
GROUP BY d.age_band_key, d.age_band_label
ORDER BY d.ordre;
