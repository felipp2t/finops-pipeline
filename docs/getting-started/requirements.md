# Requisitos e Dependências

## Requisitos de sistema

| Ferramenta | Versão mínima | Finalidade |
|---|---|---|
| Docker | 24.x | Contêineres |
| Docker Compose | v2.x (plugin) | Orquestração local |
| Git | 2.x | Controle de versão |
| Python | 3.11+ | Script de seed |
| Make | qualquer | Atalhos de comandos (opcional) |

> **RAM mínima recomendada:** 8 GB livres (Spark + Airflow + Postgres + MinIO + Metabase)  
> **Disco:** ~5 GB para imagens Docker + dados gerados

## Serviços Docker (imagens)

| Serviço | Imagem | Versão | Porta(s) |
|---|---|---|---|
| PostgreSQL | `postgres` | 15-alpine | 5432 |
| MinIO | `minio/minio` | latest | 9000, 9001 |
| Spark Master | custom (`bitnami/spark`) | 3.5.1 | 7077, 8080 |
| Spark Worker | custom (`bitnami/spark`) | 3.5.1 | — |
| JupyterLab | custom (`bitnami/spark`) | 3.5.1 | 8888 |
| Airflow Webserver | `apache/airflow` | 2.9.3-python3.11 | 8082 |
| Airflow Scheduler | `apache/airflow` | 2.9.3-python3.11 | — |
| Metabase | `metabase/metabase` | latest | 3000 |

## Dependências Python (seed script)

Instaladas via `pip` para executar o seed:

```
psycopg2-binary>=2.9.9
faker>=25.9.2
python-dateutil>=2.9.0
```

## Dependências Spark (incluídas no Dockerfile)

Os JARs abaixo são baixados durante o `docker build`:

| JAR | Versão | Finalidade |
|---|---|---|
| `delta-spark_2.12` | 3.2.0 | Delta Lake |
| `delta-storage` | 3.2.0 | Delta Lake storage |
| `hadoop-aws` | 3.3.4 | Protocolo s3a:// |
| `aws-java-sdk-bundle` | 1.12.262 | Credenciais S3A |
| `postgresql` | 42.7.3 | JDBC para Postgres |

## Dependências Python (dentro dos contêineres)

Instaladas na imagem Spark/Jupyter:

```
delta-spark==3.2.0
pyspark==3.5.1
jupyterlab==4.2.3
papermill==2.6.0
psycopg2-binary==2.9.9
boto3==1.34.144
pandas==2.2.2
faker==25.9.2
```

No Airflow:

```
apache-airflow-providers-papermill
pyspark==3.5.1
delta-spark==3.2.0
psycopg2-binary
```
