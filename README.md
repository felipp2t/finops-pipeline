# FinOps Pipeline

Pipeline de dados com **arquitetura medallion** para o domínio de **FinOps (Cloud Financial Operations)**.

![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5-E25A1C?style=flat&logo=apachespark&logoColor=white)
![Delta Lake](https://img.shields.io/badge/Delta%20Lake-3.2-003366?style=flat&logo=delta&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.9-017CEE?style=flat&logo=apacheairflow&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-S3%20Compatible-C72E49?style=flat&logo=minio&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat&logo=postgresql&logoColor=white)
![Metabase](https://img.shields.io/badge/Metabase-BI-509EE3?style=flat&logo=metabase&logoColor=white)
![Jupyter](https://img.shields.io/badge/JupyterLab-notebooks-F37626?style=flat&logo=jupyter&logoColor=white)
![Docker](https://img.shields.io/badge/Docker%20Compose-local-2496ED?style=flat&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)

## Documentação completa

Acesse a documentação em: **https://felipp2t.github.io/finops-pipeline/**

## Quickstart

```bash
git clone https://github.com/felipp2t/finops-pipeline.git
cd finops-pipeline
cp .env.example .env

docker compose build spark-master spark-worker jupyter
docker compose up -d
python scripts/02_seed.py
```

| Serviço | URL | Credenciais |
|---|---|---|
| JupyterLab | http://localhost:8888 | sem senha |
| Spark UI | http://localhost:8080 | — |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin123 |
| Airflow | http://localhost:8082 | admin / admin123 |
| Metabase | http://localhost:3000 | setup na primeira vez |

## Arquitetura

```
PostgreSQL (fonte) → Landing (JSON) → Bronze (Delta) → Silver (Delta) → Gold (Delta + Postgres) → Metabase
```

Camadas orquestradas pelo **Airflow** via `PapermillOperator`, executando notebooks `.ipynb` com **PySpark**.

## Estrutura

```
finops-pipeline/
├── docker-compose.yml
├── spark/Dockerfile
├── scripts/
│   ├── 01_schema.sql
│   └── 02_seed.py
├── notebooks/
│   ├── landing/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── dags/
└── docs/          ← MkDocs
```

## Licença

MIT
