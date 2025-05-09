import os
from datetime import datetime

from cosmos import DbtDag, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import SnowflakeUserPasswordProfileMapping

# Configuration for dbt profile
profile_config = ProfileConfig(
    profile_name="default",
    target_name="dev",
    profile_mapping=SnowflakeUserPasswordProfileMapping(
        conn_id="snowflake_conn", 
        profile_args={"database": "dbt_db", "schema": "dbt_schema"},
    )
)

# Create the DAG
dbt_snowflake_dag = DbtDag(
    # DAG configs
    dag_id="dbt_snowflake_pipeline",
    schedule_interval="@daily",
    start_date=datetime(2023, 9, 10),
    catchup=False,
    
    # dbt configs
    project_config=ProjectConfig(
        "/usr/local/airflow/dags/dbt/data_pipeline",
    ),
    profile_config=profile_config,
    execution_config=ExecutionConfig(
        dbt_executable_path=f"{os.environ.get('AIRFLOW_HOME', '/opt/airflow')}/dbt_venv/bin/dbt",
    ),
    
    # Operator configs
    operator_args={"install_deps": True},
)

# Optional: Add data quality checks
"""
from airflow.operators.python import PythonOperator

def check_data_quality():
    # Add your data quality checks here
    pass

data_quality_check = PythonOperator(
    task_id="data_quality_check",
    python_callable=check_data_quality,
    dag=dbt_snowflake_dag,
)

# Add to the end of your DAG
dbt_snowflake_dag.tasks[-1] >> data_quality_check
"""

# Optional: Add email notifications on failure
"""
from airflow.operators.email import EmailOperator

email_on_failure = EmailOperator(
    task_id="email_on_failure",
    to="your-email@example.com",
    subject="Airflow dbt Pipeline Failed",
    html_content="The dbt pipeline has failed. Please check the logs.",
    trigger_rule="one_failed",
    dag=dbt_snowflake_dag,
)

# Add to all tasks
for task in dbt_snowflake_dag.tasks:
    task >> email_on_failure
"""
