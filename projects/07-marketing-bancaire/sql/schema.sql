-- Projet 07 : schéma SQLite minimal pour la table de faits.
-- Les dimensions sont importées depuis data/processed via l'outil SQLite choisi.

DROP TABLE IF EXISTS fact_campaign;
CREATE TABLE fact_campaign (
    campaign_id INTEGER PRIMARY KEY,
    age INTEGER NOT NULL,
    age_band_key INTEGER NOT NULL,
    job_key INTEGER NOT NULL,
    marital_key INTEGER NOT NULL,
    education_key INTEGER NOT NULL,
    default_status TEXT NOT NULL,
    housing_loan TEXT NOT NULL,
    personal_loan TEXT NOT NULL,
    contact_key INTEGER NOT NULL,
    month_key INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    duration INTEGER NOT NULL,
    campaign INTEGER NOT NULL,
    campaign_band_key INTEGER NOT NULL,
    pdays INTEGER NOT NULL,
    previously_contacted INTEGER NOT NULL,
    previous INTEGER NOT NULL,
    poutcome_key INTEGER NOT NULL,
    "emp.var.rate" REAL NOT NULL,
    "cons.price.idx" REAL NOT NULL,
    "cons.conf.idx" REAL NOT NULL,
    euribor3m REAL NOT NULL,
    "nr.employed" REAL NOT NULL,
    outcome_key INTEGER NOT NULL CHECK (outcome_key IN (0, 1))
);

CREATE INDEX idx_fact_campaign_month ON fact_campaign(month_key);
CREATE INDEX idx_fact_campaign_job ON fact_campaign(job_key);
CREATE INDEX idx_fact_campaign_outcome ON fact_campaign(outcome_key);
