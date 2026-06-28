FROM apache/airflow:2.9.3-python3.11

RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-3.11.txt" \
    apache-airflow-providers-papermill \
    pyspark==3.5.1 \
    psycopg2-binary
