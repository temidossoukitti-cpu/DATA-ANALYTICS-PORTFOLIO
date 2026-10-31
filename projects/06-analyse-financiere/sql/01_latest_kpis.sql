-- Indicateurs comptables du dernier exercice disponible.
SELECT
    fy.fiscal_year_key AS fiscal_year,
    m.label_fr AS indicateur,
    m.statement AS etat,
    f.value AS valeur,
    m.unit AS unite
FROM fact_financials AS f
JOIN dim_fiscal_year AS fy ON fy.fiscal_year_key = f.fiscal_year_key
JOIN dim_metric AS m ON m.metric_key = f.metric_key
WHERE fy.fiscal_year_key = (SELECT MAX(fiscal_year_key) FROM dim_fiscal_year)
  AND f.metric_key IN ('revenue', 'operating_income', 'net_income', 'eps_diluted',
                       'total_assets', 'total_liabilities', 'equity', 'cfo', 'capex')
ORDER BY m.sort_order;
