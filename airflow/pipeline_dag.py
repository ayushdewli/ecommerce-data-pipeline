from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os

default_args = {
    "owner": "ayush",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

def run_ingestion():
    import subprocess
    import sys
    sys.path.insert(0, "/opt/ingestion")
    result = subprocess.run(
        ["python", "/opt/ingestion/ingest.py"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"Ingestion failed:\n{result.stderr}")

def validate_mongo():
    import subprocess
    result = subprocess.run(
        ["python", "-c", """
from pymongo import MongoClient
import os
client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo:27017/"))
db = client["olist_raw"]
cols = ["orders", "customers", "payments", "order_items"]
for col in cols:
    count = db[col].count_documents({})
    print(f"{col}: {count} documents")
    if count == 0:
        raise ValueError(f"{col} is empty!")
client.close()
print("MongoDB validation passed.")
"""],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"MongoDB validation failed:\n{result.stderr}")

def run_spark():
    import subprocess
    result = subprocess.run(
        [
            "spark-submit",
            "--master", "spark://spark:7077",
            "--packages",
            "org.mongodb.spark:mongo-spark-connector_2.12:3.0.2,"
            "org.postgresql:postgresql:42.6.0",
            "/opt/spark_jobs/transform.py",
        ],
        capture_output=True,
        text=True,
        timeout=600,
    )
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"Spark failed:\n{result.stderr}")

def validate_postgres():
    import subprocess
    result = subprocess.run(
        ["python", "-c", """
import psycopg2
conn = psycopg2.connect(
    host="postgres", database="ecommerce",
    user="pipeline", password="pipeline"
)
cur = conn.cursor()
for table in ["daily_revenue", "top_products", "customer_metrics"]:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    n = cur.fetchone()[0]
    print(f"{table}: {n} rows")
    if n == 0:
        raise ValueError(f"{table} is empty!")
cur.close()
conn.close()
print("PostgreSQL validation passed.")
"""],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"PostgreSQL validation failed:\n{result.stderr}")

with DAG(
    dag_id="ecommerce_pipeline",
    default_args=default_args,
    description="Olist end-to-end pipeline",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["portfolio"],
) as dag:

    t1 = PythonOperator(
        task_id="ingest_to_mongodb",
        python_callable=run_ingestion,
    )
    t2 = PythonOperator(
        task_id="validate_mongodb",
        python_callable=validate_mongo,
    )
    t3 = PythonOperator(
        task_id="spark_transform",
        python_callable=run_spark,
    )
    t4 = PythonOperator(
        task_id="validate_postgresql",
        python_callable=validate_postgres,
    )

    t1 >> t2 >> t3 >> t4