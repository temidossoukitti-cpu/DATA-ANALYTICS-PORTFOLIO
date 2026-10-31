SELECT
    COUNT(*) AS clients,
    SUM(default_next_month) AS defaults,
    AVG(CAST(default_next_month AS REAL)) AS default_rate
FROM fact_clients;
