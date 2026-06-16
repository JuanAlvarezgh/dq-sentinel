from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

import ejecutar

default_args = {"retries": 2, "retry_delay": timedelta(seconds=30)}

with DAG(
    dag_id="centinela_calidad",
    start_date=datetime(2026, 1, 1),
    schedule="@hourly",
    catchup=False,
    default_args=default_args,
    description="Valida el warehouse, persiste resultados, genera reporte y alerta a Slack.",
) as dag:
    PythonOperator(task_id="ejecutar_validaciones", python_callable=ejecutar.main)
