PRAGMA foreign_keys = ON;

CREATE TABLE dim_outcome (
    outcome_key INTEGER PRIMARY KEY,
    label_fr TEXT NOT NULL,
    is_fraud INTEGER NOT NULL CHECK (is_fraud IN (0, 1))
);

CREATE TABLE dim_amount_band (
    amount_band_key INTEGER PRIMARY KEY,
    label_fr TEXT NOT NULL,
    lower_exclusive REAL,
    upper_inclusive REAL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE dim_time_window (
    time_window_key INTEGER PRIMARY KEY,
    label_fr TEXT NOT NULL,
    start_second INTEGER NOT NULL,
    end_second_exclusive INTEGER NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY,
    time_seconds REAL NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    outcome_key INTEGER NOT NULL REFERENCES dim_outcome(outcome_key),
    amount_band_key INTEGER NOT NULL REFERENCES dim_amount_band(amount_band_key),
    time_window_key INTEGER NOT NULL REFERENCES dim_time_window(time_window_key),
    sampling_weight REAL NOT NULL CHECK (sampling_weight > 0),
    sample_partition TEXT NOT NULL CHECK (sample_partition IN ('train', 'test'))
);

CREATE TABLE fact_model_test (
    transaction_id INTEGER PRIMARY KEY REFERENCES fact_transactions(transaction_id),
    time_seconds REAL NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    outcome_key INTEGER NOT NULL REFERENCES dim_outcome(outcome_key),
    sampling_weight REAL NOT NULL CHECK (sampling_weight > 0),
    model_probability REAL NOT NULL CHECK (model_probability >= 0 AND model_probability <= 1),
    model_prediction INTEGER NOT NULL CHECK (model_prediction IN (0, 1)),
    baseline_amount_flag INTEGER NOT NULL CHECK (baseline_amount_flag IN (0, 1)),
    eval_population_weight REAL NOT NULL CHECK (eval_population_weight > 0),
    loss_severity_assumption REAL NOT NULL,
    legitimate_friction_cost_assumption REAL NOT NULL,
    expected_cost_contribution REAL NOT NULL,
    fraud_amount_missed_contribution REAL NOT NULL,
    fraud_amount_intercepted_contribution REAL NOT NULL,
    legitimate_amount_blocked_contribution REAL NOT NULL,
    amount_band_key INTEGER NOT NULL REFERENCES dim_amount_band(amount_band_key),
    time_window_key INTEGER NOT NULL REFERENCES dim_time_window(time_window_key)
);

CREATE TABLE model_scorecard (
    model_name TEXT NOT NULL,
    recommended_threshold REAL NOT NULL,
    pr_auc_test REAL NOT NULL,
    precision_test REAL NOT NULL,
    recall_test REAL NOT NULL,
    f1_test REAL NOT NULL,
    expected_cost_test REAL NOT NULL,
    test_transactions_population_estimate REAL NOT NULL,
    split_method TEXT NOT NULL,
    features_used TEXT NOT NULL
);

CREATE TABLE model_cost_sensitivity (
    loss_severity_assumption REAL NOT NULL,
    legitimate_friction_cost_assumption REAL NOT NULL,
    threshold_selected_on_training_oof REAL NOT NULL,
    test_expected_cost_estimate REAL NOT NULL,
    test_weighted_precision REAL NOT NULL,
    test_weighted_recall REAL NOT NULL,
    test_fraud_amount_missed_estimate REAL NOT NULL,
    test_legitimate_transactions_blocked_estimate REAL NOT NULL,
    cost_unit TEXT NOT NULL
);

CREATE TABLE model_money_controls (
    method TEXT NOT NULL,
    transactions_flagged_estimate REAL NOT NULL,
    legitimate_transactions_blocked_estimate REAL NOT NULL,
    fraud_transactions_intercepted_estimate REAL NOT NULL,
    fraud_transactions_missed_estimate REAL NOT NULL,
    amount_flagged_estimate REAL NOT NULL,
    fraud_amount_intercepted_estimate REAL NOT NULL,
    fraud_amount_missed_estimate REAL NOT NULL,
    legitimate_amount_blocked_estimate REAL NOT NULL,
    expected_cost_estimate REAL NOT NULL,
    missed_fraud_loss_severity_assumption REAL NOT NULL,
    legitimate_friction_cost_assumption REAL NOT NULL,
    cost_unit TEXT NOT NULL
);
