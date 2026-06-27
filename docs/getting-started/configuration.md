# Configuração — Variáveis de Ambiente

Todas as variáveis ficam no arquivo `.env` (copie de `.env.example`).

## PostgreSQL

| Variável | Padrão | Descrição |
|---|---|---|
| `POSTGRES_USER` | `finops_user` | Usuário do banco |
| `POSTGRES_PASSWORD` | `finops_pass` | Senha do banco |
| `POSTGRES_DB` | `finops` | Nome do banco principal |

O mesmo Postgres serve três propósitos:

- Schema `finops_source` — dados de origem (teams, budgets, cost_entries)
- Schema `finops_gold` — dados gold para o Metabase
- Database `airflow` — metadados do Airflow

## MinIO

| Variável | Padrão | Descrição |
|---|---|---|
| `MINIO_ROOT_USER` | `minioadmin` | Access key do MinIO |
| `MINIO_ROOT_PASSWORD` | `minioadmin123` | Secret key do MinIO |
| `MINIO_BUCKET` | `datalake` | Nome do bucket principal |

Paths das camadas dentro do bucket `datalake`:

```
s3a://datalake/landing/<entidade>/year=YYYY/month=MM/day=DD/
s3a://datalake/bronze/<entidade>/year=YYYY/month=MM/
s3a://datalake/silver/<entidade>/year=YYYY/month=MM/
s3a://datalake/gold/<mart>/year=YYYY/month=MM/
```

## Airflow

| Variável | Padrão | Descrição |
|---|---|---|
| `AIRFLOW__CORE__FERNET_KEY` | (gerado) | Chave de criptografia do Airflow |
| `AIRFLOW__WEBSERVER__SECRET_KEY` | `finops-secret-key-2025` | Chave da sessão web |
| `AIRFLOW_UID` | `50000` | UID do processo Airflow |

Credenciais padrão da interface web: `admin` / `admin123`.

## Spark

| Variável | Padrão | Descrição |
|---|---|---|
| `SPARK_MASTER_URL` | `spark://spark-master:7077` | URL do master Spark |

A SparkSession é criada em `notebooks/utils/spark_session.py` lendo estas variáveis de ambiente.

## Conexões internas (Docker network)

Dentro da rede `finops_net`, os serviços se comunicam pelos hostnames:

| Hostname | Serviço | Porta |
|---|---|---|
| `postgres` | PostgreSQL | 5432 |
| `minio` | MinIO API | 9000 |
| `spark-master` | Spark Master | 7077 |
| `airflow-webserver` | Airflow UI | 8080 |
| `metabase` | Metabase | 3000 |

## Gerar uma nova Fernet Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
