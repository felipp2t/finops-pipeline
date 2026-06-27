# Pipeline — Orquestração com Airflow

## Visão geral dos DAGs

O pipeline é composto por **4 DAGs encadeados** via `ExternalTaskSensor`. Cada DAG executa os notebooks de uma camada usando o `PapermillOperator`.

```
dag_landing  ──(schedule: 01:00 UTC diariamente)
    │
    └── dag_bronze  ──(ExternalTaskSensor aguarda dag_landing)
            │
            └── dag_silver  ──(ExternalTaskSensor aguarda dag_bronze)
                    │
                    └── dag_gold  ──(ExternalTaskSensor aguarda dag_silver)
```

## Parâmetros injetados pelo Papermill

Cada notebook recebe os parâmetros via célula marcada com a tag `parameters`:

```python
# parameters
execution_date = "2025-06-15"   # injetado pelo Airflow via {{ ds }}
year = 2025                      # injetado pelo Airflow
month = 6                        # injetado pelo Airflow
```

## DAG: `dag_landing`

**Schedule:** `0 1 * * *` (01:00 UTC)  
**Tasks:** 3 notebooks em paralelo (teams, budgets, cost_entries)

```python
landing_teams >> landing_done
landing_budgets >> landing_done
landing_cost_entries >> landing_done
```

## DAG: `dag_bronze`

**Schedule:** sem schedule fixo  
**Trigger:** `ExternalTaskSensor` aguarda `dag_landing` completar  
**Tasks:** 3 notebooks sequenciais

```python
wait_landing >> bronze_teams >> bronze_budgets >> bronze_cost_entries
```

## DAG: `dag_silver`

**Schedule:** sem schedule fixo  
**Trigger:** `ExternalTaskSensor` aguarda `dag_bronze` completar  
**Tasks:** 3 notebooks sequenciais

```python
wait_bronze >> silver_teams >> silver_budgets >> silver_cost_entries
```

## DAG: `dag_gold`

**Schedule:** sem schedule fixo  
**Trigger:** `ExternalTaskSensor` aguarda `dag_silver` completar  
**Tasks:** 4 marts em paralelo + carga Postgres

```python
wait_silver >> [gold_monthly, gold_top, gold_trend, gold_env] >> gold_load_postgres
```

## Reprocessamento parcial

Para reprocessar apenas a camada silver em diante:

1. No Airflow UI, acesse `dag_silver`
2. Clique em "Clear" na data desejada
3. O `dag_silver` reexecuta e dispara automaticamente o `dag_gold`

Para reprocessar tudo a partir da landing:

1. Limpe o run de `dag_landing` para a data desejada
2. As demais camadas reexecutam em cascata via sensor
