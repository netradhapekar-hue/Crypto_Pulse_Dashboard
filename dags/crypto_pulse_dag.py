import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime

from scripts.fetch_crypto_data import fetch_crypto_data
from scripts.data_cleaning import clean_crypto_data
from scripts.run_analysis import run_analysis

with DAG(
    dag_id="crypto_etl_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="*/15 * * * *",
    catchup=False
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_crypto",
        python_callable=fetch_crypto_data
    )

    clean_task = PythonOperator(
        task_id="clean_data",
        python_callable=clean_crypto_data
    )

    analysis_task = PythonOperator(
        task_id="run_analysis",
        python_callable=run_analysis
    )

    fetch_task >> clean_task >> analysis_task
