FROM bitnami/spark:3.5.1

USER root

# Python dependencies
RUN pip install --no-cache-dir \
    delta-spark==3.2.0 \
    pyspark==3.5.1 \
    jupyterlab==4.2.3 \
    papermill==2.6.0 \
    psycopg2-binary==2.9.9 \
    boto3==1.34.144 \
    pandas==2.2.2 \
    faker==25.9.2

# Download Delta + S3A JARs to avoid downloading on every SparkSession start
RUN curl -L -o /opt/bitnami/spark/jars/delta-spark_2.12-3.2.0.jar \
      https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.2.0/delta-spark_2.12-3.2.0.jar && \
    curl -L -o /opt/bitnami/spark/jars/delta-storage-3.2.0.jar \
      https://repo1.maven.org/maven2/io/delta/delta-storage/3.2.0/delta-storage-3.2.0.jar && \
    curl -L -o /opt/bitnami/spark/jars/hadoop-aws-3.3.4.jar \
      https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl -L -o /opt/bitnami/spark/jars/aws-java-sdk-bundle-1.12.262.jar \
      https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar && \
    curl -L -o /opt/bitnami/spark/jars/postgresql-42.7.3.jar \
      https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.3/postgresql-42.7.3.jar

USER 1001

WORKDIR /opt/spark/notebooks
