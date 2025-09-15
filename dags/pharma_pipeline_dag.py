# dags/pharma_pipeline_dag.py

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
import pendulum

# Best Practice: Define the project's base directory using an Airflow Variable.
# This makes the DAG portable across different environments.
PROJECT_DIR = "{{ var.value.pharma_project_dir }}"

with DAG(
    dag_id="pharma_data_pipeline_v1",
    start_date=pendulum.datetime(2025, 1, 1, tz="Europe/Paris"),
    schedule="@daily",
    catchup=False,
    tags=["data-eng", "pharma"],
    doc_md="""
    ### Pharmaceutical Data Pipeline
    This DAG orchestrates the full ETL process for pharmaceutical publications.
    It tests the code, runs the main pipeline, and performs ad-hoc analysis.
    """,
) as dag:

    # Task 1: Run tests as a quality gate before execution
    task_run_tests = BashOperator(
        task_id="run_tests",
        bash_command=f"cd {PROJECT_DIR} && pytest -v",
    )

    # Task 2: Run the main data pipeline script
    task_run_main_pipeline = BashOperator(
        task_id="run_main_pipeline",
        bash_command=f"cd {PROJECT_DIR} && python -m src.pharma_graph_pipeline.main",
    )

    # Task 3: Run the ad-hoc analysis script
    task_run_adhoc_analysis = BashOperator(
        task_id="run_adhoc_analysis",
        bash_command=f"cd {PROJECT_DIR} && python -m src.pharma_graph_pipeline.adhoc.analysis",
    )

    # Define the execution order
    task_run_tests >> task_run_main_pipeline >> task_run_adhoc_analysis