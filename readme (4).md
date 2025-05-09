# Modern ELT Pipeline with dbt, Snowflake, and Airflow

This repository demonstrates a modern ELT (Extract, Load, Transform) data pipeline using industry-standard tools:

- **dbt (Data Build Tool)**: For transforming data in your warehouse
- **Snowflake**: Cloud data warehouse
- **Apache Airflow**: Workflow orchestration

By following this tutorial, you'll learn how to:

1. Set up a Snowflake environment for data transformations
2. Build a dbt project with staging and mart models
3. Implement testing strategies for data quality
4. Orchestrate the entire pipeline with Apache Airflow

## Prerequisites

- A Snowflake account (free trial available at [snowflake.com](https://www.snowflake.com))
- Python 3.8+ installed
- Basic SQL knowledge
- Docker for running Airflow (optional)

## Repository Structure

```
modern-elt-pipeline/
├── .github/                     # GitHub workflows for CI/CD
├── dbt/                         # dbt project files
│   ├── macros/                  # Reusable SQL code blocks
│   ├── models/                  # SQL transformation models
│   │   ├── staging/             # Initial transformations from source
│   │   └── marts/               # Business-level transformations
│   ├── tests/                   # Custom dbt tests
│   ├── dbt_project.yml          # dbt project configuration
│   └── profiles.yml             # dbt connection profiles
├── airflow/                     # Airflow DAG files
│   ├── dags/                    # Airflow DAG definitions
│   └── Dockerfile               # Custom Airflow image
├── docs/                        # Documentation files
│   ├── images/                  # Screenshots and diagrams
│   └── tutorials/               # Step-by-step guides
├── .gitignore                   # Git ignore file
└── README.md                    # This file
```

## Getting Started

Follow these steps to set up and run the complete ELT pipeline:

1. [Set up Snowflake environment](docs/tutorials/1-snowflake-setup.md)
2. [Configure your dbt project](docs/tutorials/2-dbt-setup.md)
3. [Create source and staging models](docs/tutorials/3-staging-models.md)
4. [Implement dbt macros](docs/tutorials/4-dbt-macros.md)
5. [Build transformation models](docs/tutorials/5-transformation-models.md)
6. [Add data tests](docs/tutorials/6-testing.md)
7. [Deploy with Airflow](docs/tutorials/7-airflow-deployment.md)

## Architecture Overview

![ELT Pipeline Architecture](docs/images/elt-architecture.png)

This pipeline follows modern ELT practices:
1. **Extract** - Data is extracted from source systems (using Snowflake sample data in this example)
2. **Load** - Data is loaded into Snowflake (already done in this example with sample data)
3. **Transform** - Data is transformed using dbt with a modular approach:
   - Staging models clean and standardize source data
   - Intermediate models join and prepare data
   - Fact models create final analytics-ready tables

Airflow orchestrates the entire process on a schedule, ensuring reliable data pipeline execution.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
