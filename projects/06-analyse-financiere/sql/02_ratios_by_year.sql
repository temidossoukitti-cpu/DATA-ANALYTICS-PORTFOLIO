-- Ratios clés par exercice, en colonnes.
SELECT
    fy.fiscal_year_key AS fiscal_year,
    ROUND(MAX(CASE WHEN r.ratio_key = 'operating_margin' THEN r.value END), 6) AS marge_operationnelle,
    ROUND(MAX(CASE WHEN r.ratio_key = 'net_margin' THEN r.value END), 6) AS marge_nette,
    ROUND(MAX(CASE WHEN r.ratio_key = 'roe' THEN r.value END), 6) AS roe,
    ROUND(MAX(CASE WHEN r.ratio_key = 'roa' THEN r.value END), 6) AS roa,
    ROUND(MAX(CASE WHEN r.ratio_key = 'current_ratio' THEN r.value END), 6) AS liquidite_courante,
    ROUND(MAX(CASE WHEN r.ratio_key = 'debt_ratio' THEN r.value END), 6) AS dette_sur_actif
FROM fact_ratios AS r
JOIN dim_fiscal_year AS fy ON fy.fiscal_year_key = r.fiscal_year_key
GROUP BY fy.fiscal_year_key
ORDER BY fy.fiscal_year_key;
