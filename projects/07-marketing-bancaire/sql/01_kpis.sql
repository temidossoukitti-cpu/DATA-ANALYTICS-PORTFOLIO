-- KPI globaux
SELECT
    COUNT(*) AS campagnes,
    SUM(outcome_key) AS souscriptions,
    CAST(SUM(outcome_key) AS REAL) / COUNT(*) AS taux_conversion
FROM fact_campaign;

-- Conversion par mois
SELECT month_key, COUNT(*) AS campagnes, SUM(outcome_key) AS souscriptions,
       CAST(SUM(outcome_key) AS REAL) / COUNT(*) AS taux_conversion
FROM fact_campaign
GROUP BY month_key
ORDER BY month_key;

-- Conversion par métier
SELECT job_key, COUNT(*) AS campagnes, SUM(outcome_key) AS souscriptions,
       CAST(SUM(outcome_key) AS REAL) / COUNT(*) AS taux_conversion
FROM fact_campaign
GROUP BY job_key
ORDER BY taux_conversion DESC;

-- Contrôle des valeurs invalides
SELECT COUNT(*) AS lignes_invalides
FROM fact_campaign
WHERE outcome_key NOT IN (0, 1)
   OR campaign < 1
   OR age < 17 OR age > 100
   OR duration < 0;
