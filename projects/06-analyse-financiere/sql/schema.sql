PRAGMA foreign_keys = ON;

CREATE TABLE dim_fiscal_year (
    fiscal_year_key INTEGER PRIMARY KEY,
    period_end TEXT NOT NULL,
    label_fr TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE dim_metric (
    metric_key TEXT PRIMARY KEY,
    label_fr TEXT NOT NULL,
    statement TEXT NOT NULL,
    unit TEXT NOT NULL,
    definition TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE dim_ratio (
    ratio_key TEXT PRIMARY KEY,
    label_fr TEXT NOT NULL,
    category TEXT NOT NULL,
    unit TEXT NOT NULL,
    definition TEXT NOT NULL,
    formula TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE fact_financials (
    fiscal_year_key INTEGER NOT NULL REFERENCES dim_fiscal_year(fiscal_year_key),
    metric_key TEXT NOT NULL REFERENCES dim_metric(metric_key),
    value REAL NOT NULL,
    PRIMARY KEY (fiscal_year_key, metric_key)
);

CREATE TABLE fact_ratios (
    fiscal_year_key INTEGER NOT NULL REFERENCES dim_fiscal_year(fiscal_year_key),
    ratio_key TEXT NOT NULL REFERENCES dim_ratio(ratio_key),
    value REAL NOT NULL,
    PRIMARY KEY (fiscal_year_key, ratio_key)
);

CREATE TABLE financial_scorecard (
    entity TEXT NOT NULL,
    latest_year INTEGER NOT NULL,
    revenue REAL NOT NULL,
    operating_income REAL NOT NULL,
    net_income REAL NOT NULL,
    operating_margin REAL NOT NULL,
    net_margin REAL NOT NULL,
    roe REAL NOT NULL,
    roa REAL NOT NULL,
    current_ratio REAL NOT NULL,
    debt_ratio REAL NOT NULL,
    fcf REAL NOT NULL,
    fcf_margin REAL NOT NULL,
    eps_diluted REAL NOT NULL,
    revenue_cagr REAL NOT NULL,
    net_income_cagr REAL NOT NULL,
    period_start INTEGER NOT NULL,
    period_end INTEGER NOT NULL
);

CREATE TABLE financial_alerts (
    alert_key TEXT PRIMARY KEY,
    label_fr TEXT NOT NULL,
    unit TEXT NOT NULL,
    threshold REAL NOT NULL,
    observed REAL NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('CONFORME', 'VIGILANCE')),
    definition TEXT NOT NULL
);
