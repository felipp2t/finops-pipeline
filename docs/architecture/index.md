# Arquitetura

## Visão geral

O projeto implementa a **arquitetura medallion** (medalhão) — padrão criado pela Databricks que organiza um data lake em camadas de qualidade progressiva.

```
┌─────────────────────────────────────────────────────────────────┐
│                        ORIGEM                                   │
│  PostgreSQL (finops_source)                                     │
│  ├── finops_source.teams                                        │
│  ├── finops_source.budgets                                      │
│  └── finops_source.cost_entries                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Airflow dag_landing
                           ▼ PapermillOperator
┌─────────────────────────────────────────────────────────────────┐
│                     LANDING ZONE                                │
│  MinIO s3a://datalake/landing/                                  │
│  Formato: JSON   Partição: year/month/day                       │
│  Transformação: nenhuma — dump fiel da origem                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Airflow dag_bronze (ExternalTaskSensor)
                           ▼ PapermillOperator
┌─────────────────────────────────────────────────────────────────┐
│                     BRONZE LAYER                                │
│  MinIO s3a://datalake/bronze/                                   │
│  Formato: Delta Lake   Partição: year/month                     │
│  Transformação: tipagem, _ingested_at, _source                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Airflow dag_silver (ExternalTaskSensor)
                           ▼ PapermillOperator
┌─────────────────────────────────────────────────────────────────┐
│                     SILVER LAYER                                │
│  MinIO s3a://datalake/silver/                                   │
│  Formato: Delta Lake   Partição: year/month                     │
│  Transformação: limpeza, dedup, normalização, enriquecimento    │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Airflow dag_gold (ExternalTaskSensor)
                           ▼ PapermillOperator
┌─────────────────────────────────────────────────────────────────┐
│                      GOLD LAYER                                 │
│  MinIO s3a://datalake/gold/   (fonte canônica)                  │
│  Formato: Delta Lake   Partição: year/month                     │
│  Transformação: agregações finais — data marts                  │
│                                                                 │
│  PostgreSQL finops_gold   (serving layer para Metabase)         │
│  Carga via JDBC (overwrite mensal)                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                          BI                                     │
│  Metabase → PostgreSQL finops_gold                              │
│  4 KPIs numéricos + 2 gráficos                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Princípios da arquitetura medallion

| Camada | Qualidade | Auditoria | Consumo |
|---|---|---|---|
| Landing | Bruta | Alta (fiel à origem) | Não (só para reprocessamento) |
| Bronze | Tipada | Alta | Raramente |
| Silver | Limpa | Alta | Engenharia / Data Science |
| Gold | Agregada | Média | Analistas / BI |

## Por que Delta Lake?

- **ACID transactions** — garante consistência mesmo com falhas
- **Schema enforcement** — rejeita dados com schema incompatível
- **Time travel** — `VERSION AS OF` e `TIMESTAMP AS OF` para reprocessamento
- **Merge/Upsert** — suporte nativo a `MERGE INTO` para atualizações incrementais
- **Partition pruning** — queries filtradas por `year/month` leem só as partições relevantes

## Por que MinIO?

- API 100% compatível com Amazon S3
- Notebooks e DAGs funcionam sem alteração em produção na AWS (só muda o endpoint)
- Roda localmente via Docker sem custo
