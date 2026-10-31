-- Écart entre le dernier exercice et la moyenne de la période, par ratio.
WITH moyenne AS (
    SELECT ratio_key, AVG(value) AS moyenne
    FROM fact_ratios
    GROUP BY ratio_key
),
dernier AS (
    SELECT ratio_key, value AS valeur_recente
    FROM fact_ratios
    WHERE fiscal_year_key = (SELECT MAX(fiscal_year_key) FROM dim_fiscal_year)
)
SELECT
    d.category AS categorie,
    d.label_fr AS ratio,
    ROUND(dernier.valeur_recente, 6) AS valeur_recente,
    ROUND(moyenne.moyenne, 6) AS moyenne_periode,
    ROUND(dernier.valeur_recente - moyenne.moyenne, 6) AS ecart,
    ROUND((dernier.valeur_recente - moyenne.moyenne) / NULLIF(ABS(moyenne.moyenne), 0), 6) AS ecart_relatif
FROM dernier
JOIN moyenne ON moyenne.ratio_key = dernier.ratio_key
JOIN dim_ratio AS d ON d.ratio_key = dernier.ratio_key
ORDER BY d.sort_order;
