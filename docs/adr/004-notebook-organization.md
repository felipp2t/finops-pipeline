# ADR-004 — Organização de Notebooks

**Status:** Aceito  
**Data:** 2026-06-27  
**Decisores:** Felipe Rossetto

## Contexto

O pipeline é implementado em notebooks `.ipynb` (PySpark). A granularidade dos notebooks impacta na manutenibilidade, rastreabilidade e facilidade de reexecução parcial.

## Decisão

**Um notebook por entidade por camada.**

```
notebooks/
├── landing/
│   ├── 01_landing_teams.ipynb
│   ├── 02_landing_budgets.ipynb
│   └── 03_landing_cost_entries.ipynb
├── bronze/
│   ├── 01_bronze_teams.ipynb
│   ├── 02_bronze_budgets.ipynb
│   └── 03_bronze_cost_entries.ipynb
├── silver/
│   ├── 01_silver_teams.ipynb
│   ├── 02_silver_budgets.ipynb
│   └── 03_silver_cost_entries.ipynb
└── gold/
    ├── 01_gold_monthly_cost_by_team.ipynb
    ├── 02_gold_top_resources.ipynb
    ├── 03_gold_cost_trend_by_provider.ipynb
    ├── 04_gold_cost_by_environment.ipynb
    └── 05_gold_load_postgres.ipynb
```

### Célula `parameters` (Papermill)

Todo notebook tem uma célula marcada como `parameters` (tag via Jupyter) com os parâmetros de execução:

```python
# parameters
execution_date = "2025-06-15"
year = 2025
month = 6
```

### Utilitários compartilhados

`notebooks/utils/spark_session.py` — função `create_spark_session(app_name)` reutilizada em todos os notebooks.

## Consequências

**Positivas:**
- Falha em um notebook não bloqueia os outros da mesma camada (ex: bronze_budgets pode falhar sem afetar bronze_cost_entries)
- Cada notebook é uma unidade independente de execução no Airflow
- Fácil de debugar: abrir um notebook específico e reexecutar célula a célula

**Negativas:**
- Mais arquivos para manter (14 notebooks)
- SparkSession criada múltiplas vezes — aceitável em ambiente de estudo

## Alternativas consideradas

- **Um notebook por camada**: mais simples, mas mistura entidades — difícil de debugar e reexecutar parcialmente — descartado
- **Um notebook por DAG**: acoplamento desnecessário entre estrutura de orquestração e implementação — descartado
