# Deploying with Apache Airflow

Now that we have a complete dbt project with models and tests, we'll deploy it with Apache Airflow to automate the execution of our pipeline on a schedule.

## Understanding Airflow for dbt Orchestration

Apache Airflow is a platform to programmatically author, schedule, and monitor workflows. For our dbt pipeline, Airflow will:

1. Run our dbt models on a schedule
2. Provide monitoring and alerting
3. Handle retries and failures gracefully
4. Integrate with other data systems if needed

We'll use Astronomer Cosmos, a package that makes it easy to integrate dbt with Airflow.

## Step 1: Set Up Airflow Environment

Start by creating a new directory for your Airflow project:

```bash
mkdir airflow-dbt
cd airflow-dbt
```

## Step 2: Create a Custom Dockerfile

Create a file called `Dockerfile`:

```docker
FROM apache/airflow:2.7.1

# Install dbt in a virtual environment
RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir dbt-snowflake && deactivate

# Install required Airflow providers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

## Step 3: Create a requirements.txt File

Create a file called `requirements.txt`:

```
astronomer-cosmos
apache-airflow-providers-snowflake
```

## Step 4: Create a docker-compose.yml File

Create a file called `docker-compose.yml`: 
This file sets up 3 services that work together:
    1) Postgres - Database for Airflow's metadata
    2) Scheduler - Runs your pipelines on schedule
    3) Webserver - UI to monitor everything

```yaml
version: '3'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 5s
      retries: 5

  scheduler:
    build: .
    command: scheduler
    depends_on:
      - postgres
    env_file:
      - .env
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - ./dbt:/opt/airflow/dbt

  webserver:
    build: .
    command: webserver
    depends_on:
      - postgres
      - scheduler
    env_file:
      - .env
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - ./dbt:/opt/airflow/dbt
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 10s
      timeout: 10s
      retries: 5

volumes:
  postgres-db-volume:
```

## Step 5: Create an Environment File

Create a file called `.env`:

```
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
AIRFLOW__CORE__FERNET_KEY=
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=True
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__API__AUTH_BACKEND=airflow.api.auth.backend.basic_auth
AIRFLOW_UID=50000
```

## Step 6: Copy Your dbt Project

Copy your dbt project into the Airflow project:

```bash
mkdir -p dbt/data_pipeline
cp -r /path/to/your/dbt/project/* dbt/data_pipeline/
```

## Step 7: Create an Airflow DAG for dbt

Create a file called `dags/dbt_dag.py`:

```python
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
    start_date=datetime(2024, 9, 10),
    catchup=False,
    
    # dbt configs
    project_config=ProjectConfig(
        "/opt/airflow/dbt/data_pipeline",
    ),
    profile_config=profile_config,
    execution_config=ExecutionConfig(
        dbt_executable_path=f"{os.environ.get('AIRFLOW_HOME', '/opt/airflow')}/dbt_venv/bin/dbt",
    ),
    
    # Operator configs
    operator_args={"install_deps": True},
)
```

## Step 8: Start Airflow

Start the Airflow services:

```bash
docker-compose up -d
```

## Step 9: Configure Snowflake Connection in Airflow

1. Open the Airflow UI at http://localhost:8080 (default username/password: airflow/airflow)
2. Go to Admin > Connections
3. Click "Add a new record" to create a new connection
4. Fill in the following details:
   - Connection Id: snowflake_conn
   - Connection Type: Snowflake
   - Account: <your-account-id>
   - Login: <your-username>
   - Password: <your-password>
   - Schema: dbt_schema
   - Warehouse: dbt_wh
   - Database: dbt_db
   - Role: dbt_role
   - Extra: {"authenticator": "snowflake"}
5. Click "Save"

## Step 10: Run Your DAG

1. Go to the DAGs view in the Airflow UI
2. Find your "dbt_snowflake_pipeline" DAG
3. Enable it by clicking the toggle
4. Trigger it manually to test

## Step 11: Monitoring Your Pipeline

Once the DAG runs, you can:
1. View logs to see the output from dbt
2. Check the task durations to identify bottlenecks
3. View the DAG graph to understand the pipeline structure

## Step 12: Extending Your Pipeline (Optional)

You can extend your pipeline by adding:

1. Data quality checks after dbt runs:

```python
from airflow.operators.python import PythonOperator

def check_data_quality():
    # Check for fresh data, etc.
    pass

data_quality_check = PythonOperator(
    task_id="data_quality_check",
    python_callable=check_data_quality,
    dag=dbt_snowflake_dag,
)

# Add to the end of your DAG
dbt_snowflake_dag.tasks[-1] >> data_quality_check
```

2. Notification on failure:

```python
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
```

## Summary

In this section, we:
- Set up an Airflow environment with Docker
- Created a DAG for orchestrating our dbt pipeline
- Configured the Snowflake connection
- Learned how to monitor and extend our pipeline

By deploying our dbt project with Airflow, we've created a robust, schedulable, and monitorable ELT pipeline. This setup provides:

1. **Automation**: Regular execution of our data pipeline
2. **Monitoring**: Clear visibility into pipeline execution
3. **Error handling**: Detection and notification of failures
4. **Extensibility**: Easy integration with other data systems

This completes our end-to-end ELT pipeline with dbt, Snowflake, and Airflow.

## Resources

- [Astronomer Cosmos Documentation](https://astronomer.github.io/astronomer-cosmos/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
