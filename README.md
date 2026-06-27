# FinOps Pipeline

Pipeline de dados com **arquitetura medallion** para o domínio de **FinOps (Cloud Financial Operations)**.

**Stack:** Apache Spark · Delta Lake · Apache Airflow · MinIO · PostgreSQL · Metabase · JupyterLab · Docker Compose

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
