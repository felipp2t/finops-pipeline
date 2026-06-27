# Camadas Medallion

## Landing Zone

**Propósito:** Preservar os dados exatamente como vieram da fonte, sem nenhuma transformação.

**Detalhes técnicos:**
- Formato: **JSON** (um arquivo por execução)
- Particionamento: `year=YYYY/month=MM/day=DD/`
- Path: `s3a://datalake/landing/<entidade>/year=.../month=.../day=.../`
- Escrita: `overwrite` por data de execução

**O que os notebooks fazem:**
1. Conectam ao PostgreSQL via JDBC
2. Leem a tabela de origem com filtro de data (para landing incremental)
3. Serializam como JSON e escrevem no MinIO

**Notebooks:**
- `landing/01_landing_teams.ipynb`
- `landing/02_landing_budgets.ipynb`
- `landing/03_landing_cost_entries.ipynb`

---

## Bronze Layer

**Propósito:** Converter os dados brutos para Delta Lake com tipagem explícita. Zero regras de negócio — apenas conversão de formato.

**Detalhes técnicos:**
- Formato: **Delta Lake** (Parquet + transaction log)
- Particionamento: `year=YYYY/month=MM/`
- Path: `s3a://datalake/bronze/<entidade>/year=.../month=.../`
- Escrita: `append` (ou `mergeSchema = true`)

**Transformações aplicadas:**
- Cast de tipos (string → date, string → decimal)
- Adição de colunas de metadados: `_ingested_at`, `_source_layer`
- Normalização de nomes de colunas (snake_case)
- Sem filtragem de nulos ou regras de negócio

**Notebooks:**
- `bronze/01_bronze_teams.ipynb`
- `bronze/02_bronze_budgets.ipynb`
- `bronze/03_bronze_cost_entries.ipynb`

---

## Silver Layer

**Propósito:** Dados limpos, confiáveis e prontos para análise. Aqui aplicam-se as regras de qualidade de dados.

**Detalhes técnicos:**
- Formato: **Delta Lake**
- Particionamento: `year=YYYY/month=MM/`
- Path: `s3a://datalake/silver/<entidade>/year=.../month=.../`
- Escrita: `overwrite` por partição

**Transformações aplicadas:**
- **Deduplicação** por chave natural (ex: `(team_id, usage_date, resource_name)`)
- **Filtragem** de registros com campos obrigatórios nulos
- **Normalização** de `environment` (ex: `Production` → `prod`)
- **Enriquecimento** de `cost_entries` com campos de `teams` via join
- **Validação** de ranges (ex: `cost_usd >= 0`, `month BETWEEN 1 AND 12`)

**Notebooks:**
- `silver/01_silver_teams.ipynb`
- `silver/02_silver_budgets.ipynb`
- `silver/03_silver_cost_entries.ipynb`

---

## Gold Layer

**Propósito:** Agregações finais otimizadas para consumo analítico. É a "verdade" do negócio para o Metabase.

**Detalhes técnicos:**
- Formato: **Delta Lake** (fonte canônica) + **PostgreSQL** (serving layer)
- Particionamento: `year=YYYY/month=MM/`
- Path Delta: `s3a://datalake/gold/<mart>/year=.../month=.../`
- Carga Postgres: JDBC `overwrite` no schema `finops_gold`

**Data Marts:**

| Mart | Descrição |
|---|---|
| `monthly_cost_by_team` | Budget vs real por time × provedor × mês |
| `top_resources` | Top 10 recursos mais caros por mês |
| `cost_trend_by_provider` | Série temporal de custo por provedor com MoM |
| `cost_by_environment` | Custo por ambiente (prod/staging/dev) com % do total |

**Notebooks:**
- `gold/01_gold_monthly_cost_by_team.ipynb`
- `gold/02_gold_top_resources.ipynb`
- `gold/03_gold_cost_trend_by_provider.ipynb`
- `gold/04_gold_cost_by_environment.ipynb`
- `gold/05_gold_load_postgres.ipynb` — carga JDBC dos 4 marts no Postgres

---

## Comparativo das camadas

| Aspecto | Landing | Bronze | Silver | Gold |
|---|---|---|---|---|
| Formato | JSON | Delta | Delta | Delta + Postgres |
| Partição | year/month/day | year/month | year/month | year/month |
| Tipagem | Não (string) | Sim | Sim | Sim |
| Deduplicação | Não | Não | Sim | N/A |
| Regras de negócio | Não | Não | Sim | Sim (agregações) |
| Auditabilidade | Alta | Alta | Alta | Média |
| Quem consome | Ninguém | Eng. Dados | Data Science | Analistas / BI |
