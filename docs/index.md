# FinOps Pipeline

Pipeline de dados com **arquitetura medallion** para o domínio de **FinOps (Cloud Financial Operations)**.

## O que é este projeto?

Um pipeline de dados end-to-end que ingere dados de custos de cloud de um banco PostgreSQL, processa em múltiplas camadas de qualidade (Landing → Bronze → Silver → Gold) usando Apache Spark e Delta Lake, orquestra com Apache Airflow e entrega KPIs financeiros via Metabase.

## Tecnologias

| Componente | Tecnologia |
|---|---|
| Processamento | Apache Spark 3.5 + PySpark |
| Formato de tabela | Delta Lake 3.2 |
| Object Storage | MinIO (S3-compatible) |
| Orquestração | Apache Airflow 2.9 + PapermillOperator |
| Banco de dados | PostgreSQL 15 |
| BI / Dashboards | Metabase |
| Notebooks | JupyterLab (.ipynb) |
| Infraestrutura | Docker Compose |

## Domínio: FinOps

FinOps (Financial Operations) é a prática de otimizar custos de cloud. As entidades centrais são:

- **Teams** — times responsáveis por recursos de cloud
- **Budgets** — orçamentos mensais por time × provedor
- **Cost Entries** — lançamentos diários de custo por recurso

## Arquitetura

```
PostgreSQL (finops_source)
        │
        ▼  [Airflow dag_landing]
MinIO / landing/   ← JSON bruto
        │
        ▼  [Airflow dag_bronze]
MinIO / bronze/    ← Delta Lake + tipagem
        │
        ▼  [Airflow dag_silver]
MinIO / silver/    ← Delta Lake limpo + normalizado
        │
        ▼  [Airflow dag_gold]
MinIO / gold/      ← Delta Lake — data marts
        │
        ▼  [DAG gold: carga JDBC]
PostgreSQL (finops_gold)
        │
        ▼
Metabase Dashboard
```

## KPIs disponíveis

- **Total Spend MTD** — custo total acumulado no mês
- **Budget Utilization %** — % do orçamento consumido
- **MoM Variation %** — variação mês a mês
- **Teams Over Budget** — times que estouraram o orçamento
- **Gráfico:** tendência de custo por provedor (6 meses)
- **Gráfico:** budget vs real por time
