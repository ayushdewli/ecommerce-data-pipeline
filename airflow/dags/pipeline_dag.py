from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'ayush',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

with DAG(
    dag_id='ecommerce_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    description='End-to-end ecommerce data pipeline',
) as dag:

    ingest_to_mongodb = BashOperator(
        task_id='ingest_to_mongodb',
        bash_command='python /opt/airflow/ingestion/ingest.py',
    )

    validate_mongodb = BashOperator(
        task_id='validate_mongodb',
        bash_command='python -c "from pymongo import MongoClient; c = MongoClient(\'mongodb://mongo:27017/\'); print(\'Collections:\', c.olist_raw.list_collection_names())"',
    )

    spark_transform = BashOperator(
        task_id='spark_transform',
        bash_command='python /opt/airflow/spark/transform.py',
    )

    validate_postgresql = BashOperator(
        task_id='validate_postgresql',
        bash_command='python -c "import psycopg2; conn = psycopg2.connect(host=\'postgres\', dbname=\'ecommerce\', user=\'pipeline\', password=\'pipeline\'); cur = conn.cursor(); cur.execute(\'SELECT COUNT(*) FROM daily_revenue\'); print(\'Rows in daily_revenue:\', cur.fetchone()[0])"',
    )

    ingest_to_mongodb >> validate_mongodb >> spark_transform >> validate_postgresql