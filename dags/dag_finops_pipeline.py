# pyright: reportMissingImports=false, reportAttributeAccessIssue=false
# Os imports do Airflow só resolvem dentro do container (a pasta ./airflow do repo
# sombreia o pacote real do Airflow na análise estática local). Validado em runtime.
"""
DAG FinOps Pipeline — fluxo único medallion (Landing → Bronze → Silver → Gold).

Acionamento manual. Encadeia as 4 camadas num só DAG:
  landing (3 em paralelo)
    → bronze (teams → budgets → cost_entries)
    → silver (teams → budgets → cost_entries)
    → gold (4 marts em paralelo → carga no Postgres)

Notas:
- Bronze/Silver são sequenciais (cost_entries depende de teams para o enriquecimento)
  e para evitar contenção de recursos no Spark (1 worker atende 1 app por vez).
- Os 4 marts da gold rodam em paralelo e convergem na carga JDBC do Postgres.
"""

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.papermill.operators.papermill import PapermillOperator

for _layer in ("landing", "bronze", "silver", "gold"):
    os.makedirs(f"/tmp/papermill/{_layer}", exist_ok=True)

NOTEBOOKS_PATH = "/opt/airflow/notebooks"

default_args = {
    "owner": "data-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


def papermill_task(layer: str, task_id: str, notebook: str) -> PapermillOperator:
    return PapermillOperator(
        task_id=task_id,
        input_nb=f"{NOTEBOOKS_PATH}/{layer}/{notebook}",
        output_nb=f"/tmp/papermill/{layer}/{notebook.replace('.ipynb', '')}_{{{{ ds }}}}.ipynb",
        parameters={
            "execution_date": "{{ ds }}",
            "year": "{{ execution_date.year }}",
            "month": "{{ execution_date.month }}",
            "day": "{{ execution_date.day }}",
        },
    )


with DAG(
    dag_id="dag_finops_pipeline",
    description="Pipeline FinOps medallion completo (Landing → Bronze → Silver → Gold)",
    schedule=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["finops", "medallion", "pipeline"],
) as dag:

    # ── Landing — extração Postgres → CSV no MinIO (paralelo) ──
    landing_teams = papermill_task("landing", "landing_teams", "01_landing_teams.ipynb")
    landing_budgets = papermill_task("landing", "landing_budgets", "02_landing_budgets.ipynb")
    landing_cost_entries = papermill_task("landing", "landing_cost_entries", "03_landing_cost_entries.ipynb")

    # ── Bronze — CSV → Delta com tipagem (sequencial) ──
    bronze_teams = papermill_task("bronze", "bronze_teams", "01_bronze_teams.ipynb")
    bronze_budgets = papermill_task("bronze", "bronze_budgets", "02_bronze_budgets.ipynb")
    bronze_cost_entries = papermill_task("bronze", "bronze_cost_entries", "03_bronze_cost_entries.ipynb")

    # ── Silver — data quality + enriquecimento (teams antes para o join) ──
    silver_teams = papermill_task("silver", "silver_teams", "01_silver_teams.ipynb")
    silver_budgets = papermill_task("silver", "silver_budgets", "02_silver_budgets.ipynb")
    silver_cost_entries = papermill_task("silver", "silver_cost_entries", "03_silver_cost_entries.ipynb")

    # ── Gold — marts agregados (paralelo) → carga no Postgres ──
    gold_monthly = papermill_task("gold", "gold_monthly_cost_by_team", "01_gold_monthly_cost_by_team.ipynb")
    gold_top = papermill_task("gold", "gold_top_resources", "02_gold_top_resources.ipynb")
    gold_trend = papermill_task("gold", "gold_cost_trend_by_provider", "03_gold_cost_trend_by_provider.ipynb")
    gold_env = papermill_task("gold", "gold_cost_by_environment", "04_gold_cost_by_environment.ipynb")
    gold_load_postgres = papermill_task("gold", "gold_load_postgres", "05_gold_load_postgres.ipynb")

    # ── Encadeamento entre camadas ──
    [landing_teams, landing_budgets, landing_cost_entries] >> bronze_teams
    bronze_teams >> bronze_budgets >> bronze_cost_entries >> silver_teams
    silver_teams >> silver_budgets >> silver_cost_entries
    silver_cost_entries >> [gold_monthly, gold_top, gold_trend, gold_env] >> gold_load_postgres
