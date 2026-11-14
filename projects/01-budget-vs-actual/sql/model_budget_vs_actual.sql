-- Projet 1 : Budget vs Actual Finance Dashboard
-- SQL = langage utilisé pour interroger et organiser des données.
-- Ce script suppose que le fichier préparé est importé dans une table staging.

-- Table staging : copie de travail importée depuis le CSV préparé.
CREATE TABLE staging_budget_actual (
    budget_fiscal_year INTEGER NOT NULL,
    thru_quarter INTEGER NOT NULL,
    dept_rollup TEXT NOT NULL,
    dept_rollup_name TEXT NOT NULL,
    department_code TEXT NOT NULL,
    department_name TEXT NOT NULL,
    fund_code TEXT NOT NULL,
    fund_name TEXT NOT NULL,
    program_code TEXT NOT NULL,
    program_name TEXT NOT NULL,
    activity_code TEXT NOT NULL,
    activity_name TEXT NOT NULL,
    unit_code TEXT NOT NULL,
    unit_name TEXT NOT NULL,
    expense_code TEXT NOT NULL,
    expense_name TEXT NOT NULL,
    budget NUMERIC(18,2) NOT NULL,
    expenditures NUMERIC(18,2) NOT NULL,
    variance NUMERIC(18,2),
    variance_pct NUMERIC(12,4),
    budget_zero_flag BOOLEAN NOT NULL,
    negative_amount_flag BOOLEAN NOT NULL,
    unfavorable_flag BOOLEAN NOT NULL,
    period_label TEXT NOT NULL,
    key TEXT NOT NULL
);

-- Vue de contrôle : dépenses regroupées par département.
CREATE VIEW vw_department_budget_actual AS
SELECT
    budget_fiscal_year,
    thru_quarter,
    dept_rollup_name,
    department_name,
    SUM(budget) AS total_budget,
    SUM(expenditures) AS total_expenditures,
    SUM(expenditures) - SUM(budget) AS total_variance,
    CASE
        WHEN SUM(budget) = 0 THEN NULL
        ELSE (SUM(expenditures) - SUM(budget)) / SUM(budget) * 100
    END AS total_variance_pct,
    SUM(CASE WHEN unfavorable_flag THEN 1 ELSE 0 END) AS unfavorable_line_count
FROM staging_budget_actual
GROUP BY budget_fiscal_year, thru_quarter, dept_rollup_name, department_name;

-- Contrôles qualité de base.
SELECT COUNT(*) AS row_count FROM staging_budget_actual;
SELECT COUNT(DISTINCT key) AS distinct_key_count FROM staging_budget_actual;
SELECT COUNT(*) AS duplicate_key_count
FROM staging_budget_actual
GROUP BY key
HAVING COUNT(*) > 1;
SELECT COUNT(*) AS missing_amount_count
FROM staging_budget_actual
WHERE budget IS NULL OR expenditures IS NULL;
