SELECT
    SUM(CASE WHEN default_next_month = 1 THEN limit_bal ELSE 0 END) AS defaulter_credit_limit_exposure_ntd,
    SUM(limit_bal) AS total_credit_limit_ntd
FROM fact_clients;
