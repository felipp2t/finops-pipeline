# ADR-003 — Estrutura de DAGs do Airflow

**Status:** Aceito  
**Data:** 2026-06-27  
**Decisores:** Felipe Rossetto

## Contexto

O Airflow precisa orquestrar as 4 camadas do pipeline (landing, bronze, silver, gold). A decisão é entre um DAG único com tasks sequenciais ou DAGs separados por camada.

## Decisão

**Um DAG por camada** com encadeamento via `ExternalTaskSensor`.

```
dag_landing  (schedule: daily @01:00)
    └── dag_bronze  (trigger: ExternalTaskSensor aguarda dag_landing.all_done)
        └── dag_silver  (trigger: ExternalTaskSensor aguarda dag_bronze.all_done)
            └── dag_gold  (trigger: ExternalTaskSensor aguarda dag_silver.all_done)
```

### Executor de Notebooks

`PapermillOperator` com os seguintes parâmetros injetados via célula `parameters`:
- `execution_date`: data de execução do DAG (`{{ ds }}`)
- `year`: `{{ execution_date.year }}`
- `month`: `{{ execution_date.month }}`

### Schedule

- `dag_landing`: `0 1 * * *` (01:00 UTC diariamente)
- `dag_bronze`, `dag_silver`, `dag_gold`: sem schedule fixo — acionados pelo sensor

## Consequências

**Positivas:**
- Reprocessamento granular: se silver falha, pode-se reexecutar só a partir do silver sem reprocessar landing + bronze
- Cada DAG tem seu próprio histórico de execução no Airflow UI
- Isolamento de falhas por camada

**Negativas:**
- `ExternalTaskSensor` é mais complexo de configurar do que `TriggerDagRunOperator`
- Mais DAGs = mais overhead de gerenciamento no Airflow

## Alternativas consideradas

- **DAG único**: mais simples, mas perda de granularidade de reprocessamento — descartado
- **TriggerDagRunOperator**: mais simples que ExternalTaskSensor, mas o DAG filho não fica vinculado ao run do pai no histórico — descartado
