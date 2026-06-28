FROM apache/spark:3.5.5-scala2.12-java11-python3-r-ubuntu

USER root

# Python dependencies (pyspark já está na imagem apache/spark — não reinstalar)
RUN pip install --no-cache-dir \
    delta-spark==3.2.0 \
    jupyterlab \
    papermill \
    psycopg2-binary \
    boto3 \
    pandas \
    faker

# Download Delta + S3A JARs to /opt/spark/jars (SPARK_HOME da imagem oficial)
RUN curl -L -o /opt/spark/jars/delta-spark_2.12-3.2.0.jar \
      https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.2.0/delta-spark_2.12-3.2.0.jar && \
    curl -L -o /opt/spark/jars/delta-storage-3.2.0.jar \
      https://repo1.maven.org/maven2/io/delta/delta-storage/3.2.0/delta-storage-3.2.0.jar && \
    curl -L -o /opt/spark/jars/hadoop-aws-3.3.4.jar \
      https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl -L -o /opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar \
      https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar && \
    curl -L -o /opt/spark/jars/postgresql-42.7.3.jar \
      https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.3/postgresql-42.7.3.jar

RUN mkdir -p /opt/spark/notebooks && chown spark:spark /opt/spark/notebooks && \
    mkdir -p /home/spark && chown spark:spark /home/spark

ENV HOME=/home/spark

USER spark

WORKDIR /opt/spark/notebooks
