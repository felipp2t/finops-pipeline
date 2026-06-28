FROM apache/airflow:2.9.3-python3.11

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jdk-headless curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/default-java

# JARs necessários para o PySpark no modo client:
# - PostgreSQL JDBC (leitura da origem e escrita gold)
# - Delta Lake (extensões de catálogo)
# - Hadoop AWS + SDK (acesso ao MinIO via s3a://)
RUN mkdir -p /opt/spark-jars && \
    curl -L -o /opt/spark-jars/postgresql-42.7.3.jar \
      https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.3/postgresql-42.7.3.jar && \
    curl -L -o /opt/spark-jars/delta-spark_2.12-3.2.0.jar \
      https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.2.0/delta-spark_2.12-3.2.0.jar && \
    curl -L -o /opt/spark-jars/delta-storage-3.2.0.jar \
      https://repo1.maven.org/maven2/io/delta/delta-storage/3.2.0/delta-storage-3.2.0.jar && \
    curl -L -o /opt/spark-jars/hadoop-aws-3.3.4.jar \
      https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl -L -o /opt/spark-jars/aws-java-sdk-bundle-1.12.262.jar \
      https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar && \
    chown -R airflow:root /opt/spark-jars

USER airflow

# Providers instalados com constraints oficiais (garante compatibilidade com Airflow 2.9.3)
RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-3.11.txt" \
    apache-airflow-providers-papermill \
    psycopg2-binary

# PySpark separado — constraints do Airflow pinavam 3.5.1, mas driver e worker devem ter a mesma versão
RUN pip install --no-cache-dir pyspark==3.5.5
