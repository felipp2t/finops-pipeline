# ADR-002 — Storage: MinIO + Delta Lake

**Status:** Aceito  
**Data:** 2026-06-27  
**Decisores:** Felipe Rossetto

## Contexto

O pipeline precisa de um storage para as camadas intermediárias (landing, bronze, silver, gold). Em produção, seria um cloud storage (S3, GCS, ADLS). O projeto roda localmente via Docker Compose.

## Decisão

Usar **MinIO** como object storage S3-compatible e **Delta Lake** como formato de tabela.

### Configuração MinIO

- Bucket único: `datalake`
- Prefixos por camada: `landing/`, `bronze/`, `silver/`, `gold/`
- Protocolo: `s3a://datalake/<camada>/<entidade>/`
- Acesso via `hadoop-aws` com `fs.s3a.path.style.access = true`

### Particionamento Delta Lake

Esquema: `year=<YYYY>/month=<MM>/`

Justificativa: granularidade alinhada com o ciclo de orçamento mensal de FinOps. Queries mais frequentes filtram por mês (`WHERE year=2025 AND month=06`), logo o partition pruning elimina partições inteiras.

### Versões

- Delta Lake: `3.2.0` (delta-spark_2.12)
- Hadoop AWS: `3.3.4`
- AWS Java SDK Bundle: `1.12.262`

## Consequências

**Positivas:**
- MinIO é 100% compatível com S3 API — notebooks rodam sem alteração em produção na AWS
- Delta Lake oferece ACID, time travel e schema enforcement
- `spark.jars.packages` baixa dependências automaticamente no primeiro start

**Negativas:**
- First start demora para baixar os JARs (~500MB); cache em volume resolve nos runs seguintes
- MinIO não suporta S3 Glacier — irrelevante para o projeto

## Alternativas consideradas

- **LocalFileSystem**: mais simples, mas não simula ambiente de produção — descartado
- **Apache Iceberg**: alternativa válida ao Delta, mas Delta tem melhor integração nativa com PySpark — descartado
