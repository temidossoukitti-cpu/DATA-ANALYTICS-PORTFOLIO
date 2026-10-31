-- Croissance annuelle des produits, du résultat net et du BPA.
WITH series AS (
    SELECT
        fy.fiscal_year_key AS fiscal_year,
        MAX(CASE WHEN f.metric_key = 'revenue' THEN f.value END) AS revenue,
        MAX(CASE WHEN f.metric_key = 'net_income' THEN f.value END) AS net_income,
        MAX(CASE WHEN f.metric_key = 'eps_diluted' THEN f.value END) AS eps_diluted
    FROM fact_financials AS f
    JOIN dim_fiscal_year AS fy ON fy.fiscal_year_key = f.fiscal_year_key
    GROUP BY fy.fiscal_year_key
)
SELECT
    fiscal_year,
    revenue,
    net_income,
    eps_diluted,
    ROUND((revenue - LAG(revenue) OVER (ORDER BY fiscal_year))
          / LAG(revenue) OVER (ORDER BY fiscal_year), 6) AS croissance_produits,
    ROUND((net_income - LAG(net_income) OVER (ORDER BY fiscal_year))
          / LAG(net_income) OVER (ORDER BY fiscal_year), 6) AS croissance_resultat_net,
    ROUND((eps_diluted - LAG(eps_diluted) OVER (ORDER BY fiscal_year))
          / LAG(eps_diluted) OVER (ORDER BY fiscal_year), 6) AS croissance_bpa
FROM series
ORDER BY fiscal_year;
