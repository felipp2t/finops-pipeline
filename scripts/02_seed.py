"""
Seed script — gera 6 meses de dados FinOps sintéticos no PostgreSQL.

Uso: python scripts/02_seed.py

Requer:
    pip install psycopg2-binary faker python-dateutil
"""

import os
import random
import json
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker

fake = Faker("pt_BR")
random.seed(42)

# ─── Configuração ────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "dbname": os.getenv("POSTGRES_DB", "finops"),
    "user": os.getenv("POSTGRES_USER", "finops_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "finops_pass"),
}

SEED_MONTHS = 6  # meses de histórico
END_DATE = date.today().replace(day=1) - timedelta(days=1)   # fim do mês anterior
START_DATE = END_DATE - relativedelta(months=SEED_MONTHS - 1)
START_DATE = START_DATE.replace(day=1)

# ─── Dados de referência ─────────────────────────────────────────────────────
TEAMS = [
    {"name": "Platform",  "cost_center": "CC-001", "department": "Engineering",  "owner_email": "platform@company.com"},
    {"name": "Data",      "cost_center": "CC-002", "department": "Engineering",  "owner_email": "data@company.com"},
    {"name": "Frontend",  "cost_center": "CC-003", "department": "Product",      "owner_email": "frontend@company.com"},
    {"name": "Backend",   "cost_center": "CC-004", "department": "Engineering",  "owner_email": "backend@company.com"},
    {"name": "Mobile",    "cost_center": "CC-005", "department": "Product",      "owner_email": "mobile@company.com"},
    {"name": "ML",        "cost_center": "CC-006", "department": "Data Science", "owner_email": "ml@company.com"},
    {"name": "Security",  "cost_center": "CC-007", "department": "Engineering",  "owner_email": "security@company.com"},
    {"name": "DevOps",    "cost_center": "CC-008", "department": "Engineering",  "owner_email": "devops@company.com"},
]

PROVIDERS = ["AWS", "GCP", "Azure"]

RESOURCE_TYPES = {
    "AWS":   ["EC2", "S3", "RDS", "Lambda", "EKS", "CloudFront", "ElastiCache"],
    "GCP":   ["Compute Engine", "Cloud Storage", "BigQuery", "Cloud Run", "GKE", "Cloud SQL"],
    "Azure": ["Virtual Machines", "Blob Storage", "SQL Database", "Functions", "AKS", "Redis Cache"],
}

REGIONS = {
    "AWS":   ["us-east-1", "us-west-2", "sa-east-1", "eu-west-1"],
    "GCP":   ["us-central1", "southamerica-east1", "europe-west1"],
    "Azure": ["eastus", "brazilsouth", "westeurope"],
}

ENVIRONMENTS = ["prod", "staging", "dev"]
ENV_WEIGHTS  = [0.60, 0.25, 0.15]

# Custo base diário por resource_type (USD) — base realista
DAILY_COST_BASE = {
    "EC2": (5.0, 80.0), "S3": (0.5, 15.0), "RDS": (8.0, 60.0),
    "Lambda": (0.1, 5.0), "EKS": (10.0, 120.0), "CloudFront": (1.0, 20.0),
    "ElastiCache": (3.0, 30.0),
    "Compute Engine": (4.0, 70.0), "Cloud Storage": (0.3, 10.0),
    "BigQuery": (2.0, 50.0), "Cloud Run": (0.5, 15.0), "GKE": (8.0, 100.0),
    "Cloud SQL": (5.0, 45.0),
    "Virtual Machines": (5.0, 85.0), "Blob Storage": (0.4, 12.0),
    "SQL Database": (7.0, 55.0), "Functions": (0.1, 4.0), "AKS": (9.0, 110.0),
    "Redis Cache": (2.0, 25.0),
}

# Budget mensal por time × provedor (USD) — alguns times vão estourar intencionalmente
BUDGET_TABLE = {
    "Platform": {"AWS": 8000, "GCP": 3000, "Azure": 2000},
    "Data":     {"AWS": 5000, "GCP": 7000, "Azure": 1500},
    "Frontend": {"AWS": 1000, "GCP":  500, "Azure":  800},
    "Backend":  {"AWS": 4000, "GCP": 2000, "Azure": 1000},
    "Mobile":   {"AWS":  800, "GCP":  400, "Azure":  600},
    "ML":       {"AWS": 3000, "GCP": 9000, "Azure": 2000},
    "Security": {"AWS": 1500, "GCP":  800, "Azure": 1200},
    "DevOps":   {"AWS": 2500, "GCP": 1000, "Azure": 1500},
}


def generate_resource_name(resource_type: str, team: str) -> str:
    team_slug = team.lower()
    suffixes = {
        "EC2": f"ec2-{team_slug}-{fake.lexify('????')}",
        "S3": f"s3-{team_slug}-{fake.lexify('????')}",
        "RDS": f"rds-{team_slug}-db",
        "Lambda": f"fn-{team_slug}-{fake.word()}",
        "EKS": f"eks-{team_slug}-cluster",
        "CloudFront": f"cf-{team_slug}-dist",
        "ElastiCache": f"redis-{team_slug}",
        "Compute Engine": f"vm-{team_slug}-{fake.lexify('????')}",
        "Cloud Storage": f"gs-{team_slug}-bucket",
        "BigQuery": f"bq-{team_slug}-dataset",
        "Cloud Run": f"run-{team_slug}-svc",
        "GKE": f"gke-{team_slug}-cluster",
        "Cloud SQL": f"sql-{team_slug}-db",
        "Virtual Machines": f"vm-{team_slug}-{fake.lexify('????')}",
        "Blob Storage": f"blob-{team_slug}-container",
        "SQL Database": f"sqldb-{team_slug}",
        "Functions": f"fn-{team_slug}-{fake.word()}",
        "AKS": f"aks-{team_slug}-cluster",
        "Redis Cache": f"redis-{team_slug}",
    }
    return suffixes.get(resource_type, f"res-{team_slug}-unknown")


def daily_cost(resource_type: str, environment: str, month_index: int) -> float:
    """Custo diário com variação por ambiente e tendência de crescimento mensal."""
    lo, hi = DAILY_COST_BASE.get(resource_type, (1.0, 20.0))
    base = random.uniform(lo, hi)

    # Ambientes não-prod têm custo menor
    env_multiplier = {"prod": 1.0, "staging": 0.3, "dev": 0.15}[environment]

    # Crescimento de ~5% ao mês (simula crescimento natural de cloud spend)
    growth = 1 + (month_index * 0.05)

    # Ruído diário ±15%
    noise = random.uniform(0.85, 1.15)

    return round(base * env_multiplier * growth * noise, 4)


def generate_cost_entries(team_id: int, team: dict, start: date, end: date):
    rows = []
    team_name = team["name"]

    # Cada time usa 2 provedores principais e 1 secundário
    primary_providers = random.sample(PROVIDERS, 2)
    secondary_provider = [p for p in PROVIDERS if p not in primary_providers][0]

    provider_weights = {p: 0.40 for p in primary_providers}
    provider_weights[secondary_provider] = 0.20

    # 3-5 recursos fixos por time × provedor (recursos persistentes)
    resources = {}
    for provider in PROVIDERS:
        rtypes = random.sample(RESOURCE_TYPES[provider], min(4, len(RESOURCE_TYPES[provider])))
        resources[provider] = [
            {
                "name": generate_resource_name(rt, team_name),
                "type": rt,
                "region": random.choice(REGIONS[provider]),
                "env": random.choices(ENVIRONMENTS, weights=ENV_WEIGHTS)[0],
            }
            for rt in rtypes
        ]

    current = start
    month_index = 0
    current_month = (current.year, current.month)

    while current <= end:
        if (current.year, current.month) != current_month:
            month_index += 1
            current_month = (current.year, current.month)

        for provider in PROVIDERS:
            # Cada provider tem chance de ter custo neste dia
            if random.random() > provider_weights.get(provider, 0.20):
                current = current + timedelta(days=1)
                break

            for res in resources[provider]:
                if random.random() < 0.90:  # 90% de dias ativos por recurso
                    cost = daily_cost(res["type"], res["env"], month_index)
                    rows.append((
                        team_id,
                        res["name"],
                        res["type"],
                        provider,
                        res["region"],
                        res["env"],
                        current,
                        cost,
                        "USD",
                        json.dumps({"team": team_name, "env": res["env"], "provider": provider}),
                    ))
        current += timedelta(days=1)

    return rows


def main():
    print(f"Conectando ao Postgres em {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # ── Teams ──────────────────────────────────────────────────────────────
    print("Inserindo teams...")
    execute_values(
        cur,
        """
        INSERT INTO finops_source.teams (name, cost_center, department, owner_email)
        VALUES %s
        ON CONFLICT (name) DO NOTHING
        RETURNING id, name
        """,
        [(t["name"], t["cost_center"], t["department"], t["owner_email"]) for t in TEAMS],
    )
    conn.commit()

    cur.execute("SELECT id, name FROM finops_source.teams ORDER BY id")
    team_rows = cur.fetchall()
    team_map = {name: tid for tid, name in team_rows}
    print(f"  {len(team_map)} times inseridos.")

    # ── Budgets ────────────────────────────────────────────────────────────
    print("Inserindo budgets (6 meses × 8 times × 3 providers)...")
    budget_rows = []
    current_month = START_DATE.replace(day=1)
    end_month = END_DATE.replace(day=1)

    while current_month <= end_month:
        for team in TEAMS:
            tid = team_map[team["name"]]
            for provider in PROVIDERS:
                base_budget = BUDGET_TABLE[team["name"]][provider]
                # Pequena variação mensal no budget (±10%)
                monthly_budget = round(base_budget * random.uniform(0.90, 1.10), 2)
                budget_rows.append((
                    tid,
                    current_month.year,
                    current_month.month,
                    provider,
                    monthly_budget,
                ))
        current_month += relativedelta(months=1)

    execute_values(
        cur,
        """
        INSERT INTO finops_source.budgets (team_id, year, month, provider, amount_usd)
        VALUES %s
        ON CONFLICT (team_id, year, month, provider) DO NOTHING
        """,
        budget_rows,
    )
    conn.commit()
    print(f"  {len(budget_rows)} registros de budget inseridos.")

    # ── Cost Entries ───────────────────────────────────────────────────────
    print(f"Gerando cost_entries de {START_DATE} até {END_DATE}...")
    all_cost_rows = []
    for team in TEAMS:
        tid = team_map[team["name"]]
        rows = generate_cost_entries(tid, team, START_DATE, END_DATE)
        all_cost_rows.extend(rows)
        print(f"  {team['name']}: {len(rows)} lançamentos")

    print(f"Inserindo {len(all_cost_rows)} cost_entries no Postgres...")
    execute_values(
        cur,
        """
        INSERT INTO finops_source.cost_entries
            (team_id, resource_name, resource_type, provider, region, environment,
             usage_date, cost_usd, currency, tags)
        VALUES %s
        """,
        all_cost_rows,
        page_size=1000,
    )
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM finops_source.cost_entries")
    total = cur.fetchone()[0]
    print(f"\nSeed concluido! Total de cost_entries: {total:,}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
