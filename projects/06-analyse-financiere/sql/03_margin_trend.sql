-- Marges et taux d'imposition effectif par exercice.
SELECT
    fy.fiscal_year_key AS fiscal_year,
    ROUND(MAX(CASE WHEN r.ratio_key = 'operating_margin' THEN r.value END), 6) AS marge_operationnelle,
    ROUND(MAX(CASE WHEN r.ratio_key = 'net_margin' THEN r.value END), 6) AS marge_nette,
    ROUND(MAX(CASE WHEN r.ratio_key = 'effective_tax_rate' THEN r.value END), 6) AS taux_imposition_effectif
FROM fact_ratios AS r
JOIN dim_fiscal_year AS fy ON fy.fiscal_year_key = r.fiscal_year_key
GROUP BY fy.fiscal_year_key
ORDER BY fy.fiscal_year_key;
