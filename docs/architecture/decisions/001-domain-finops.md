# ADR-001 — Domínio: FinOps

**Status:** Aceito  
**Data:** 2026-06-27  
**Decisores:** Felipe Rossetto

## Contexto

O projeto precisa de um domínio de negócio real para demonstrar o pipeline de dados com arquitetura medallion. O domínio escolhido deve ter entidades com relacionamentos claros, volume de dados suficiente para análise temporal e casos de uso de BI relevantes.

## Decisão

Adotamos **FinOps (Financial Operations de Cloud)** como domínio de negócio.

## Entidades centrais

- `teams` — times responsáveis por recursos de cloud
- `budgets` — orçamentos mensais por time × provedor
- `cost_entries` — lançamentos diários de custo por recurso

## Consequências

**Positivas:**
- Domínio amplamente conhecido em empresas que usam cloud
- Entidades com relacionamentos naturais (team → budget, team → cost_entries)
- Dados de série temporal (custo diário) são ideais para demonstrar particionamento e queries analíticas
- Casos de uso de BI claros: budget vs real, ranking de recursos, tendência MoM

**Negativas:**
- Seed data precisa ser sintético (não há dump público de custos reais de cloud)
- Requer seed de 6 meses para que os gráficos sejam interessantes

## Alternativas consideradas

- E-commerce: descartado por ser muito comum em demos
- RH: descartado por ter dados sensíveis que complicam o seed
- Logística: descartado por requerer dados geoespaciais adicionais
