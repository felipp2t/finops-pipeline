"""Utilitário compartilhado: cria SparkSession configurada para Delta Lake + MinIO."""

import os
import psycopg2
from datetime import datetime
from pyspark.sql import SparkSession


def _find_jars() -> str:
    """Localiza os JARs no ambiente (Airflow: /opt/spark-jars, Jupyter: /opt/spark/jars)."""
    jar_names = [
        "postgresql-42.7.3.jar",
        "delta-spark_2.12-3.2.0.jar",
        "delta-storage-3.2.0.jar",
        "hadoop-aws-3.3.4.jar",
        "aws-java-sdk-bundle-1.12.262.jar",
    ]
    for base in ["/opt/spark-jars", "/opt/spark/jars"]:
        found = [f"{base}/{j}" for j in jar_names if os.path.exists(f"{base}/{j}")]
        if found:
            return ":".join(found)
    return ""


def create_spark_session(app_name: str) -> SparkSession:
    jars = _find_jars()
    builder = (
        SparkSession.builder
        .appName(app_name)
        .master(os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077"))
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        # MinIO / S3A
        .config("spark.hadoop.fs.s3a.endpoint", os.getenv("MINIO_ENDPOINT", "http://minio:9000"))
        .config("spark.hadoop.fs.s3a.access.key", os.getenv("MINIO_ACCESS_KEY", "minioadmin"))
        .config("spark.hadoop.fs.s3a.secret.key", os.getenv("MINIO_SECRET_KEY", "minioadmin123"))
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.aws.credentials.provider",
                "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
        # Performance
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.default.parallelism", "8")
    )
    if jars:
        jars_csv = jars.replace(":", ",")
        # PYSPARK_SUBMIT_ARGS é lido antes da JVM iniciar — garante que os JARs
        # estejam no classpath do driver em modo client (Airflow/PapermillOperator)
        os.environ.setdefault("PYSPARK_SUBMIT_ARGS", f"--jars {jars_csv} pyspark-shell")
        builder = builder.config("spark.jars", jars_csv)
    return builder.getOrCreate()


def postgres_jdbc_url() -> str:
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db   = os.getenv("POSTGRES_DB", "finops")
    return f"jdbc:postgresql://{host}:{port}/{db}"


def postgres_props() -> dict:
    return {
        "user": os.getenv("POSTGRES_USER", "finops_user"),
        "password": os.getenv("POSTGRES_PASSWORD", "finops_pass"),
        "driver": "org.postgresql.Driver",
    }


def _pg_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "finops"),
        user=os.getenv("POSTGRES_USER", "finops_user"),
        password=os.getenv("POSTGRES_PASSWORD", "finops_pass"),
    )


def get_watermark(entity: str, default: str = "1970-01-01 00:00:00") -> str:
    """Retorna o último timestamp processado para a entidade.

    Se não houver watermark registrado (primeira execução), retorna `default`,
    o que faz a query retornar todos os registros existentes.
    """
    with _pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT last_processed_at FROM finops_source.pipeline_watermarks WHERE entity = %s",
                (entity,),
            )
            row = cur.fetchone()
    return str(row[0]) if row else default


def update_watermark(entity: str, new_watermark: datetime, row_count: int = 0) -> None:
    """Grava ou atualiza o watermark da entidade após extração bem-sucedida."""
    with _pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO finops_source.pipeline_watermarks
                    (entity, last_processed_at, last_run_rows, updated_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (entity) DO UPDATE SET
                    last_processed_at = EXCLUDED.last_processed_at,
                    last_run_rows     = EXCLUDED.last_run_rows,
                    updated_at        = NOW()
                """,
                (entity, new_watermark, row_count),
            )
        conn.commit()
