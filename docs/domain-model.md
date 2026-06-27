# Domain Model — FinOps Pipeline

## Entidades (PostgreSQL — schema `finops_source`)

```
┌──────────────────────────┐         ┌────────────────────────────────┐
│          teams           │         │            budgets             │
├──────────────────────────┤         ├────────────────────────────────┤
│ id           SERIAL PK   │◄────────│ id           SERIAL PK         │
│ name         VARCHAR(100)│  1   N  │ team_id      INT FK            │
│ cost_center  VARCHAR(20) │         │ year         INT               │
│ department   VARCHAR(100)│         │ month        INT               │
│ owner_email  VARCHAR(255)│         │ provider     VARCHAR(10)       │
│ created_at   TIMESTAMP   │         │ amount_usd   NUMERIC(12,2)     │
└──────────────────────────┘         │ created_at   TIMESTAMP         │
            │                        └────────────────────────────────┘
            │ 1
            │
            │ N
┌───────────────────────────────────────────────────────┐
│                     cost_entries                      │
├───────────────────────────────────────────────────────┤
│ id              SERIAL PK                             │
│ team_id         INT FK → teams.id                     │
│ resource_name   VARCHAR(200)                          │
│ resource_type   VARCHAR(100)                          │
│ provider        VARCHAR(10)   -- AWS | GCP | Azure    │
│ region          VARCHAR(50)                           │
│ environment     VARCHAR(20)   -- prod | staging | dev │
│ usage_date      DATE                                  │
│ cost_usd        NUMERIC(10,4)                         │
│ currency        VARCHAR(3)    -- always USD           │
│ tags            JSONB                                 │
│ created_at      TIMESTAMP                             │
└───────────────────────────────────────────────────────┘
```

## Camadas do Data Lake (MinIO — bucket `datalake`)

```
datalake/
├── landing/                      # JSON bruto extraído do Postgres
│   ├── teams/
│   │   └── year=2025/month=01/day=15/teams.json
│   ├── budgets/
│   │   └── year=2025/month=01/day=15/budgets.json
│   └── cost_entries/
│       └── year=2025/month=01/day=15/cost_entries.json
│
├── bronze/                       # Delta Lake — tipagem, sem transformações
│   ├── teams/                    # partitioned by year/month
│   ├── budgets/
│   └── cost_entries/
│       └── year=2025/month=01/
│
├── silver/                       # Delta Lake — limpo, normalizado, enriquecido
│   ├── teams/
│   ├── budgets/
│   └── cost_entries/
│       └── year=2025/month=01/
│
└── gold/                         # Delta Lake — marts agregados
    ├── monthly_cost_by_team/
    ├── top_resources/
    ├── cost_trend_by_provider/
    └── cost_by_environment/
```

## Gold Layer — Data Marts

### `monthly_cost_by_team`
Agregação mensal de custo real vs budget por time e provedor.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| year | INT | Ano |
| month | INT | Mês |
| team_id | INT | ID do time |
| team_name | VARCHAR | Nome do time |
| provider | VARCHAR | Provedor (AWS/GCP/Azure) |
| total_cost_usd | DECIMAL | Custo real acumulado no mês |
| budget_usd | DECIMAL | Budget aprovado |
| budget_utilization_pct | DECIMAL | (custo/budget)×100 |
| is_over_budget | BOOLEAN | custo > budget |

### `top_resources`
Top recursos por custo no mês.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| year | INT | Ano |
| month | INT | Mês |
| resource_name | VARCHAR | Nome do recurso |
| resource_type | VARCHAR | Tipo (EC2, RDS, etc.) |
| team_name | VARCHAR | Time responsável |
| provider | VARCHAR | Provedor |
| total_cost_usd | DECIMAL | Custo total no mês |
| rank | INT | Ranking (1 = mais caro) |

### `cost_trend_by_provider`
Série temporal mensal de custo por provedor.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| year | INT | Ano |
| month | INT | Mês |
| provider | VARCHAR | Provedor |
| total_cost_usd | DECIMAL | Custo total |
| prev_month_cost_usd | DECIMAL | Custo mês anterior |
| mom_variation_pct | DECIMAL | Variação MoM % |

### `cost_by_environment`
Custo mensal por ambiente (prod vs dev/staging).

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| year | INT | Ano |
| month | INT | Mês |
| environment | VARCHAR | prod / staging / dev |
| total_cost_usd | DECIMAL | Custo total |
| pct_of_total | DECIMAL | % do custo total |

## KPIs para Metabase (4 numéricos + 2 gráficos)

```
Painel FinOps Overview
├── [KPI 1] Total Spend MTD         → SUM(cost_usd) mês corrente
├── [KPI 2] Budget Utilization %    → AVG(budget_utilization_pct) mês corrente
├── [KPI 3] MoM Variation %         → AVG(mom_variation_pct) último mês completo
├── [KPI 4] Teams Over Budget        → COUNT(is_over_budget = true) mês corrente
├── [Chart 1] Custo por Provedor 6M → LINE CHART — cost_trend_by_provider
└── [Chart 2] Budget vs Real/Time   → BAR CHART  — monthly_cost_by_team mês corrente
```

## Fluxo de Dados

```
PostgreSQL (finops_source)
        │
        │ [Landing DAG — extrai JSON]
        ▼
MinIO / landing/year=/month=/day=/
        │
        │ [Bronze DAG — Delta + tipagem]
        ▼
MinIO / bronze/ (Delta Lake, particionado por year/month)
        │
        │ [Silver DAG — limpeza + normalização]
        ▼
MinIO / silver/ (Delta Lake, deduplicado)
        │
        │ [Gold DAG — agregações]
        ▼
MinIO / gold/ (Delta Lake, marts)
        │
        │ [Gold DAG — carga no Postgres]
        ▼
PostgreSQL (finops_gold schema)
        │
        │ [Metabase query]
        ▼
Dashboard BI
```
