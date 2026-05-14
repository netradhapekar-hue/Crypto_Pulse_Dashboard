import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')
    )
)

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from datetime import datetime, timedelta

from scripts.fetch_crypto_data import fetch_crypto_data
from scripts.data_cleaning import clean_crypto_data
from scripts.run_analysis import run_analysis

# =====================================================
# DEFAULT DAG SETTINGS
# =====================================================

default_args = {

    "owner": "airflow",

    "depends_on_past": False,

    "retries": 2,

    "retry_delay": timedelta(minutes=2)

}

# =====================================================
# SAFE TASK WRAPPERS
# =====================================================

def safe_fetch_crypto_data():

    try:
        fetch_crypto_data()

    except Exception as e:
        print(f"❌ Fetch task failed: {e}")
        raise


def safe_clean_crypto_data():

    try:
        clean_crypto_data()

    except Exception as e:
        print(f"❌ Cleaning task failed: {e}")
        raise


def safe_run_analysis():

    try:
        run_analysis()

    except Exception as e:
        print(f"❌ Analysis task failed: {e}")
        raise

# =====================================================
# DAG
# =====================================================

with DAG(

    dag_id="crypto_etl_pipeline",

    start_date=datetime(2024, 1, 1),

    schedule="*/15 * * * *",

    catchup=False,

    default_args=default_args,

    dagrun_timeout=timedelta(minutes=30),

    tags=["crypto", "etl", "analytics"]

) as dag:

    # =================================================
    # FETCH TASK
    # =================================================

    fetch_task = PythonOperator(

        task_id="fetch_crypto",

        python_callable=safe_fetch_crypto_data

    )

    # =================================================
    # CLEAN TASK
    # =================================================

    clean_task = PythonOperator(

        task_id="clean_data",

        python_callable=safe_clean_crypto_data

    )

    # =================================================
    # ANALYSIS TASK
    # =================================================

    analysis_task = PythonOperator(

        task_id="run_analysis",

        python_callable=safe_run_analysis

    )

    # =================================================
    # PIPELINE FLOW
    # =================================================

    fetch_task >> clean_task >> analysis_task
