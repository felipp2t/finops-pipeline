# ADR-005 — Gold Layer: Delta Lake + Carga no Postgres

**Status:** Aceito  
**Data:** 2026-06-27  
**Decisores:** Felipe Rossetto

## Contexto

O Metabase precisa de uma fonte de dados para construir dashboards. As opções são conectar diretamente ao MinIO (via Spark Thrift Server ou Trino) ou carregar os dados gold em um banco relacional.

## Decisão

Os dados Gold são escritos em **Delta Lake no MinIO** (fonte canônica) e também **carregados no PostgreSQL** (`finops_gold` schema) para consumo pelo Metabase.

### Fluxo do notebook `05_gold_load_postgres.ipynb`

1. Lê as 4 tabelas gold do Delta Lake no MinIO
2. Escreve no Postgres via JDBC (modo `overwrite`) no schema `finops_gold`
3. Tabelas Postgres: `monthly_cost_by_team`, `top_resources`, `cost_trend_by_provider`, `cost_by_environment`

### Conexão Metabase → Postgres

- Host: `postgres`
- Database: `finops`
- Schema: `finops_gold`
- User: `finops_user` (read-only para o Metabase)

## Consequências

**Positivas:**
- Metabase tem suporte nativo a Postgres — zero configuração extra
- Postgres como serving layer é mais rápido para queries do Metabase do que ler Delta diretamente
- Delta Lake no MinIO permanece como fonte canônica (auditável, com time travel)

**Negativas:**
- Dupla escrita: Delta + Postgres. Aceito pois são camadas com funções diferentes (storage vs serving)
- Carga JDBC adiciona latência ao DAG gold

## Alternativas consideradas

- **Trino + Delta**: mais próximo de produção, mas adiciona outro serviço ao Docker Compose — descartado por complexidade
- **Spark Thrift Server**: expõe SQL sobre Delta, mas Metabase precisa de driver JDBC Hive — descartado por fricção de setup
- **Metabase direto no MinIO**: não suportado nativamente — descartado
