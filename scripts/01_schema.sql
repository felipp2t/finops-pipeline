-- =============================================================
-- FinOps Pipeline — Schema inicial
-- Banco: finops | Schemas: finops_source, finops_gold
-- =============================================================

-- Banco para o Airflow (criado separadamente via env)
SELECT 'CREATE DATABASE airflow'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow')\gexec

-- Schema da fonte de dados
CREATE SCHEMA IF NOT EXISTS finops_source;

-- Schema do gold layer (serving para o Metabase)
CREATE SCHEMA IF NOT EXISTS finops_gold;

-- =============================================================
-- TABELAS DE ORIGEM (finops_source)
-- =============================================================

CREATE TABLE IF NOT EXISTS finops_source.teams (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE,
    cost_center   VARCHAR(20)  NOT NULL,
    department    VARCHAR(100) NOT NULL,
    owner_email   VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS finops_source.budgets (
    id            SERIAL PRIMARY KEY,
    team_id       INT          NOT NULL REFERENCES finops_source.teams(id),
    year          INT          NOT NULL,
    month         INT          NOT NULL CHECK (month BETWEEN 1 AND 12),
    provider      VARCHAR(10)  NOT NULL CHECK (provider IN ('AWS', 'GCP', 'Azure')),
    amount_usd    NUMERIC(12,2) NOT NULL CHECK (amount_usd > 0),
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW(),
    UNIQUE (team_id, year, month, provider)
);

CREATE TABLE IF NOT EXISTS finops_source.cost_entries (
    id             SERIAL PRIMARY KEY,
    team_id        INT          NOT NULL REFERENCES finops_source.teams(id),
    resource_name  VARCHAR(200) NOT NULL,
    resource_type  VARCHAR(100) NOT NULL,
    provider       VARCHAR(10)  NOT NULL CHECK (provider IN ('AWS', 'GCP', 'Azure')),
    region         VARCHAR(50)  NOT NULL,
    environment    VARCHAR(20)  NOT NULL CHECK (environment IN ('prod', 'staging', 'dev')),
    usage_date     DATE         NOT NULL,
    cost_usd       NUMERIC(10,4) NOT NULL CHECK (cost_usd >= 0),
    currency       VARCHAR(3)   NOT NULL DEFAULT 'USD',
    tags           JSONB,
    created_at     TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cost_entries_team_date
    ON finops_source.cost_entries (team_id, usage_date);

CREATE INDEX IF NOT EXISTS idx_cost_entries_provider_date
    ON finops_source.cost_entries (provider, usage_date);

CREATE INDEX IF NOT EXISTS idx_cost_entries_date
    ON finops_source.cost_entries (usage_date);

-- =============================================================
-- TABELAS GOLD (finops_gold — serving para Metabase)
-- Criadas vazias; preenchidas pelo notebook 05_gold_load_postgres
-- =============================================================

CREATE TABLE IF NOT EXISTS finops_gold.monthly_cost_by_team (
    year                    INT,
    month                   INT,
    team_id                 INT,
    team_name               VARCHAR(100),
    provider                VARCHAR(10),
    total_cost_usd          NUMERIC(14,4),
    budget_usd              NUMERIC(14,2),
    budget_utilization_pct  NUMERIC(8,2),
    is_over_budget          BOOLEAN,
    loaded_at               TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS finops_gold.top_resources (
    year            INT,
    month           INT,
    resource_name   VARCHAR(200),
    resource_type   VARCHAR(100),
    team_name       VARCHAR(100),
    provider        VARCHAR(10),
    total_cost_usd  NUMERIC(14,4),
    rank            INT,
    loaded_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS finops_gold.cost_trend_by_provider (
    year                INT,
    month               INT,
    provider            VARCHAR(10),
    total_cost_usd      NUMERIC(14,4),
    prev_month_cost_usd NUMERIC(14,4),
    mom_variation_pct   NUMERIC(8,2),
    loaded_at           TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS finops_gold.cost_by_environment (
    year            INT,
    month           INT,
    environment     VARCHAR(20),
    total_cost_usd  NUMERIC(14,4),
    pct_of_total    NUMERIC(8,2),
    loaded_at       TIMESTAMP DEFAULT NOW()
);
