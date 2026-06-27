# Como rodar o projeto

## 1. Clone e configure

```bash
git clone https://github.com/felipp2t/finops-pipeline.git
cd finops-pipeline

# Copie e ajuste as variáveis de ambiente
cp .env.example .env
```

As variáveis padrão do `.env.example` funcionam sem alteração para desenvolvimento local.

## 2. Build das imagens Spark

O build baixa os JARs do Delta Lake e S3A (~500 MB). Faça isso uma vez:

```bash
docker compose build spark-master spark-worker jupyter
```

> **Tempo estimado:** 3–8 minutos dependendo da conexão.

## 3. Suba a infraestrutura

```bash
docker compose up -d postgres minio minio-init
```

Aguarde o Postgres ficar healthy:

```bash
docker compose ps   # postgres deve mostrar "healthy"
```

## 4. Execute o seed de dados

O seed gera 6 meses de dados FinOps sintéticos (~20 mil registros):

```bash
# Instale as dependências locais do seed (uma vez)
pip install psycopg2-binary faker python-dateutil

# Execute o seed
python scripts/02_seed.py
```

Ou via Docker (sem instalar Python local):

```bash
docker compose exec postgres psql -U finops_user -d finops -f /docker-entrypoint-initdb.d/01_schema.sql
docker compose run --rm -e POSTGRES_HOST=postgres jupyter python /opt/spark/notebooks/../../../scripts/02_seed.py
```

> O schema SQL é executado automaticamente pelo Postgres na primeira inicialização via `scripts/01_schema.sql`.

## 5. Suba todos os serviços

```bash
docker compose up -d
```

## 6. Acesse as interfaces

| Serviço | URL | Credenciais |
|---|---|---|
| **JupyterLab** | http://localhost:8888 | sem senha |
| **Spark Web UI** | http://localhost:8080 | — |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin123 |
| **Airflow** | http://localhost:8082 | admin / admin123 |
| **Metabase** | http://localhost:3000 | setup na primeira vez |

## 7. Execute o pipeline manualmente (JupyterLab)

Abra o JupyterLab em http://localhost:8888 e execute os notebooks na ordem:

```
landing/01_landing_teams.ipynb
landing/02_landing_budgets.ipynb
landing/03_landing_cost_entries.ipynb

bronze/01_bronze_teams.ipynb
bronze/02_bronze_budgets.ipynb
bronze/03_bronze_cost_entries.ipynb

silver/01_silver_teams.ipynb
silver/02_silver_budgets.ipynb
silver/03_silver_cost_entries.ipynb

gold/01_gold_monthly_cost_by_team.ipynb
gold/02_gold_top_resources.ipynb
gold/03_gold_cost_trend_by_provider.ipynb
gold/04_gold_cost_by_environment.ipynb
gold/05_gold_load_postgres.ipynb
```

## 8. Execute via Airflow

1. Acesse http://localhost:8082
2. Ative o DAG `dag_landing`
3. Dispare manualmente clicando em "Trigger DAG"
4. Os demais DAGs (`dag_bronze`, `dag_silver`, `dag_gold`) disparam automaticamente via `ExternalTaskSensor`

## 9. Configure o Metabase

1. Acesse http://localhost:3000
2. Siga o wizard de setup
3. Adicione uma conexão PostgreSQL:
   - **Host:** `postgres`
   - **Port:** `5432`
   - **Database:** `finops`
   - **User:** `finops_user`
   - **Password:** `finops_pass`
4. Selecione o schema `finops_gold`
5. Crie perguntas usando as tabelas `monthly_cost_by_team`, `top_resources`, `cost_trend_by_provider`, `cost_by_environment`

## Comandos úteis

```bash
# Ver logs de um serviço
docker compose logs -f airflow-scheduler

# Parar tudo
docker compose down

# Parar e remover volumes (reset completo)
docker compose down -v

# Acessar Postgres
docker compose exec postgres psql -U finops_user -d finops

# Verificar dados do seed
docker compose exec postgres psql -U finops_user -d finops \
  -c "SELECT COUNT(*) FROM finops_source.cost_entries;"

# Listar arquivos no MinIO
docker compose exec minio mc ls local/datalake --recursive
```

## Estrutura de diretórios

```
finops-pipeline/
├── docker-compose.yml          # Orquestração dos serviços
├── .env.example                # Variáveis de ambiente (copie para .env)
├── spark/
│   └── Dockerfile              # Imagem Spark + Delta + MinIO jars
├── scripts/
│   ├── 01_schema.sql           # Schema PostgreSQL
│   └── 02_seed.py              # Gerador de dados sintéticos
├── notebooks/
│   ├── utils/spark_session.py  # Utilitário compartilhado
│   ├── landing/                # Extração Postgres → MinIO JSON
│   ├── bronze/                 # JSON → Delta Lake
│   ├── silver/                 # Limpeza e normalização
│   └── gold/                   # Agregações e carga Postgres
├── dags/                       # DAGs do Airflow
└── docs/                       # Documentação MkDocs
```
