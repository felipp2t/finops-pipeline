# Progresso do Projeto — FinOps Pipeline

## O que é o projeto

Pipeline de dados com **arquitetura medallion** (Landing → Bronze → Silver → Gold) para o domínio de **FinOps** (gestão de custos de cloud). Os dados vêm de um PostgreSQL, passam pelas camadas Delta Lake no MinIO, são orquestrados pelo Airflow via PapermillOperator e entregues ao Metabase via schema `finops_gold`.

---

## Stack definida

| Componente | Tecnologia |
|---|---|
| Processamento | Apache Spark 3.5.5 + PySpark |
| Formato de tabela | Delta Lake 3.2 |
| Object Storage | MinIO (S3-compatible) |
| Orquestração | Apache Airflow 2.9.3 + PapermillOperator |
| Banco de dados | PostgreSQL 15 |
| BI | Metabase |
| Notebooks | JupyterLab (.ipynb) |
| Infra | Docker Compose |

---

## Domínio: FinOps

**Entidades no PostgreSQL (`finops_source`):**
- `teams` — 8 times (Platform, Data, Frontend, Backend, Mobile, ML, Security, DevOps)
- `budgets` — orçamentos mensais por time × provedor (AWS/GCP/Azure) — 144 registros
- `cost_entries` — lançamentos diários de custo por recurso — ~2.700 registros (seed de 6 meses)

**Controle de pipeline:**
- `pipeline_watermarks` — watermark por entidade para ingestão incremental

---

## O que foi criado

### Documentação
- MkDocs com tema Material configurado (`mkdocs.yml`)
- `docs/` completo: arquitetura, modelo relacional (ER), camadas medallion, quickstart, configuração, glossário, referências
- 5 ADRs (domínio, storage, DAGs, notebooks, gold+postgres)

### Infraestrutura
- `docker-compose.yml` com 9 serviços: Postgres, MinIO, Spark Master/Worker, JupyterLab, Airflow (init/webserver/scheduler), Metabase
- `spark/Dockerfile` — baseado em `apache/spark:3.5.5-scala2.12-java11-python3-r-ubuntu` com JARs Delta Lake e S3A embutidos
- `airflow/Dockerfile` — baseado em `apache/airflow:2.9.3-python3.11` com Java JDK, JARs necessários e providers pinados via constraints oficial

### Banco de dados
- `scripts/01_schema.sql` — schemas `finops_source` e `finops_gold`, tabelas, índices e watermarks
- `scripts/02_seed.py` — gera 6 meses de dados FinOps sintéticos (Faker, seed=42, reproduzível)

### Notebooks (14 no total)
- **Landing** (3): extração sem Spark — psycopg2 + boto3, salva CSV flat no MinIO com watermark incremental
- **Bronze** (3): lê CSV do MinIO, aplica tipagem, escreve Delta Lake
- **Silver** (3): deduplicação, normalização de `environment`, enriquecimento com `team_name`
- **Gold** (5): 4 data marts agregados + carga JDBC no PostgreSQL para o Metabase

### DAGs Airflow (4)
- `dag_landing` — schedule 01:00 UTC, 3 tasks em paralelo
- `dag_bronze/silver/gold` — sem schedule, acionados por ExternalTaskSensor em cadeia

### Utilitários
- `notebooks/utils/spark_session.py` — SparkSession configurada para Delta+MinIO, watermark helpers

---

## Status atual

| Camada | Status |
|---|---|
| Landing (teams) | ✅ Funcionando — salva CSV no MinIO |
| Landing (budgets) | ✅ Funcionando |
| Landing (cost_entries) | ✅ Funcionando — ~2.700 registros, um CSV por dia |
| Bronze | 🔜 Não testado ainda |
| Silver | 🔜 Não testado ainda |
| Gold | 🔜 Não testado ainda |
| Metabase | 🔜 Não configurado |

---

## Decisões importantes tomadas

- **Landing sem Spark**: a landing usa psycopg2+boto3 direto (sem JVM/JAR) — mais simples e sem problemas de classpath no Airflow
- **CSV flat no landing**: `landing/teams/teams_2026-06-28.csv` em vez de Hive-style `year=/month=/day=`
- **Watermark por `created_at`**: captura registros tardios (custo reportado com atraso pelo provedor)
- **Imagem Airflow customizada**: Dockerfile próprio com Java + JARs + constraints oficiais para evitar upgrade acidental do Airflow
- **`apache/spark` no lugar de `bitnami/spark`**: bitnami virou produto pago; oficial da Apache está no Docker Hub
- **Gold → Postgres**: Delta Lake é a fonte canônica, Postgres é o serving layer para o Metabase

---

## Problemas resolvidos no caminho

1. `bitnami/spark` removido do Docker Hub → migrou para `apache/spark:3.5.5`
2. Airflow pip install upgradava o próprio Airflow → Dockerfile customizado com `--constraint` oficial
3. `ClassNotFoundException: org.postgresql.Driver` no Airflow → landing reescrita sem Spark
4. `ModuleNotFoundError: utils` → sys.path configurado antes dos imports
5. Watermark de teams/budgets avançado sem arquivos no MinIO → reset manual via SQL
