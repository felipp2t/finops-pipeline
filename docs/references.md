# Referências

## Documentação oficial

| Tecnologia | Link |
|---|---|
| Apache Spark | https://spark.apache.org/docs/latest/ |
| Delta Lake | https://docs.delta.io/latest/index.html |
| Apache Airflow | https://airflow.apache.org/docs/ |
| MinIO | https://min.io/docs/minio/container/index.html |
| Metabase | https://www.metabase.com/docs/latest/ |
| Papermill | https://papermill.readthedocs.io/en/latest/ |
| PySpark | https://spark.apache.org/docs/latest/api/python/ |

## Conceitos

| Conceito | Link |
|---|---|
| Arquitetura Medallion (Databricks) | https://www.databricks.com/glossary/medallion-architecture |
| FinOps Foundation | https://www.finops.org/introduction/what-is-finops/ |
| Delta Lake — Quick Start | https://docs.delta.io/latest/quick-start.html |
| S3A FileSystem (hadoop-aws) | https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html |

## Compatibilidade de versões

| Spark | Delta Lake | Scala | Python |
|---|---|---|---|
| 3.5.x | 3.2.x | 2.12 | 3.11 |
| 3.4.x | 2.4.x | 2.12 | 3.10 |

> **Importante:** Delta Lake e Spark precisam ter versões compatíveis. Consulte a [tabela de compatibilidade oficial](https://docs.delta.io/latest/releases.html).

## Tutoriais relacionados

- Delta Lake com MinIO: https://delta.io/blog/delta-lake-minio/
- Airflow + Papermill: https://airflow.apache.org/docs/apache-airflow-providers-papermill/
- PySpark com Delta Lake: https://docs.delta.io/latest/quick-start.html#python

## Configuração S3A para MinIO

```python
spark.hadoop.fs.s3a.endpoint          = http://minio:9000
spark.hadoop.fs.s3a.access.key        = minioadmin
spark.hadoop.fs.s3a.secret.key        = minioadmin123
spark.hadoop.fs.s3a.path.style.access = true
spark.hadoop.fs.s3a.impl              = org.apache.hadoop.fs.s3a.S3AFileSystem
```
