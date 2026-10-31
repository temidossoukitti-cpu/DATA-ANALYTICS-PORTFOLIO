PRAGMA foreign_keys = ON;

CREATE TABLE dim_age_band (
    age_band_key INTEGER PRIMARY KEY,
    age_band_label TEXT NOT NULL UNIQUE,
    ordre INTEGER NOT NULL
);

CREATE TABLE dim_education (
    education_key INTEGER PRIMARY KEY,
    education_code INTEGER NOT NULL UNIQUE,
    education_label TEXT NOT NULL
);

CREATE TABLE dim_marriage (
    marriage_key INTEGER PRIMARY KEY,
    marriage_code INTEGER NOT NULL UNIQUE,
    marriage_label TEXT NOT NULL
);

CREATE TABLE dim_limit_band (
    limit_band_key INTEGER PRIMARY KEY,
    limit_band_label TEXT NOT NULL UNIQUE,
    lower_limit REAL NOT NULL,
    upper_limit REAL NOT NULL,
    clients INTEGER NOT NULL
);

CREATE TABLE dim_pay_status (
    pay_status_key INTEGER PRIMARY KEY,
    pay_code INTEGER NOT NULL UNIQUE,
    pay_status_label TEXT NOT NULL
);

CREATE TABLE dim_risk_band (
    risk_band_key INTEGER PRIMARY KEY,
    risk_band_label TEXT NOT NULL UNIQUE,
    probability_min REAL NOT NULL,
    probability_max REAL NOT NULL,
    ordre INTEGER NOT NULL
);

CREATE TABLE model_scorecard (
    scorecard_key INTEGER PRIMARY KEY,
    random_state INTEGER NOT NULL,
    train_fraction REAL NOT NULL,
    test_fraction REAL NOT NULL,
    train_clients INTEGER NOT NULL,
    test_clients INTEGER NOT NULL,
    test_default_rate REAL NOT NULL,
    decision_threshold REAL NOT NULL,
    roc_auc REAL NOT NULL,
    pr_auc_average_precision REAL NOT NULL,
    ks_statistic REAL NOT NULL,
    precision_at_threshold REAL NOT NULL,
    recall_at_threshold REAL NOT NULL,
    brier_score REAL NOT NULL,
    true_negative INTEGER NOT NULL,
    false_positive INTEGER NOT NULL,
    false_negative INTEGER NOT NULL,
    true_positive INTEGER NOT NULL,
    base_lgd_assumption REAL NOT NULL,
    risk_band_cutoffs TEXT NOT NULL,
    protected_features_excluded TEXT NOT NULL
);

CREATE TABLE fact_clients (
    client_id INTEGER PRIMARY KEY,
    limit_bal REAL NOT NULL,
    sex INTEGER NOT NULL,
    education INTEGER NOT NULL,
    marriage INTEGER NOT NULL,
    age INTEGER NOT NULL,
    pay_0 INTEGER NOT NULL,
    pay_2 INTEGER NOT NULL,
    pay_3 INTEGER NOT NULL,
    pay_4 INTEGER NOT NULL,
    pay_5 INTEGER NOT NULL,
    pay_6 INTEGER NOT NULL,
    bill_amt1 REAL NOT NULL,
    bill_amt2 REAL NOT NULL,
    bill_amt3 REAL NOT NULL,
    bill_amt4 REAL NOT NULL,
    bill_amt5 REAL NOT NULL,
    bill_amt6 REAL NOT NULL,
    pay_amt1 REAL NOT NULL,
    pay_amt2 REAL NOT NULL,
    pay_amt3 REAL NOT NULL,
    pay_amt4 REAL NOT NULL,
    pay_amt5 REAL NOT NULL,
    pay_amt6 REAL NOT NULL,
    default_next_month INTEGER NOT NULL CHECK (default_next_month IN (0, 1)),
    education_original INTEGER NOT NULL,
    marriage_original INTEGER NOT NULL,
    age_band TEXT NOT NULL,
    age_band_key INTEGER NOT NULL,
    limit_band_key INTEGER NOT NULL,
    limit_band TEXT NOT NULL,
    education_key INTEGER NOT NULL,
    marriage_key INTEGER NOT NULL,
    pay_status_key INTEGER NOT NULL,
    utilization_raw REAL,
    utilization REAL NOT NULL,
    utilization_band TEXT NOT NULL,
    payment_ratio_m1 REAL,
    max_delay_6m INTEGER NOT NULL,
    n_delays_6m INTEGER NOT NULL,
    risk_flag_recent_delay INTEGER NOT NULL CHECK (risk_flag_recent_delay IN (0, 1)),
    predicted_pd REAL NOT NULL,
    risk_band_key INTEGER NOT NULL,
    model_partition TEXT NOT NULL CHECK (model_partition IN ('Train', 'Test')),
    FOREIGN KEY (age_band_key) REFERENCES dim_age_band(age_band_key),
    FOREIGN KEY (education_key) REFERENCES dim_education(education_key),
    FOREIGN KEY (marriage_key) REFERENCES dim_marriage(marriage_key),
    FOREIGN KEY (limit_band_key) REFERENCES dim_limit_band(limit_band_key),
    FOREIGN KEY (pay_status_key) REFERENCES dim_pay_status(pay_status_key),
    FOREIGN KEY (risk_band_key) REFERENCES dim_risk_band(risk_band_key)
);

CREATE INDEX idx_fact_age_band ON fact_clients(age_band_key);
CREATE INDEX idx_fact_education ON fact_clients(education_key);
CREATE INDEX idx_fact_marriage ON fact_clients(marriage_key);
CREATE INDEX idx_fact_limit_band ON fact_clients(limit_band_key);
CREATE INDEX idx_fact_pay_status ON fact_clients(pay_status_key);
CREATE INDEX idx_fact_risk_band ON fact_clients(risk_band_key);
CREATE INDEX idx_fact_partition ON fact_clients(model_partition);
