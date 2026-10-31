SELECT
    d.pay_code,
    d.pay_status_label,
    COUNT(*) AS clients,
    SUM(f.default_next_month) AS defaults,
    AVG(CAST(f.default_next_month AS REAL)) AS default_rate
FROM fact_clients AS f
JOIN dim_pay_status AS d ON d.pay_status_key = f.pay_status_key
GROUP BY d.pay_code, d.pay_status_label
ORDER BY d.pay_code;
