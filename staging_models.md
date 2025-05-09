# Creating Source and Staging Models

In this section, we'll define our data sources and create staging models that transform raw data into a more usable format.

## Understanding Sources and Staging Models

- **Sources** represent the raw data available in your data warehouse.
- **Staging models** perform initial transformations like renaming columns, type casting, and basic cleaning.

## Step 1: Define Your Sources

Create a file called `models/staging/tpch_sources.yml` to define the source tables:

```yaml
version: 2

sources:
  - name: tpch
    database: snowflake_sample_data
    schema: tpch_sf1
    tables:
      - name: orders
        columns:
          - name: o_orderkey
            tests:
              - unique
              - not_null
      - name: lineitem
        columns:
          - name: l_orderkey
            tests:
              - relationships:
                  to: source('tpch', 'orders')
                  field: o_orderkey
```

This YAML file:
- Defines a source named `tpch` that points to Snowflake's sample data
- Specifies two tables: `orders` and `lineitem`
- Includes tests to ensure data quality:
  - `o_orderkey` should be unique and not null
  - `l_orderkey` in the lineitem table should exist in the orders table

## Step 2: Create Staging Model for Orders

Create a file called `models/staging/stg_tpch_orders.sql`:

```sql
select
    o_orderkey as order_key,
    o_custkey as customer_key,
    o_orderstatus as status_code,
    o_totalprice as total_price,
    o_orderdate as order_date
from
    {{ source('tpch', 'orders') }}
```

This model:
- Selects specific columns from the orders table
- Renames columns to follow a consistent naming convention
- Uses the `source()` function to reference the source defined in our YAML file

## Step 3: Create Staging Model for Line Items

Create a file called `models/staging/stg_tpch_line_items.sql`:

```sql
select
    {{
        dbt_utils.generate_surrogate_key([
            'l_orderkey',
            'l_linenumber'
        ])
    }} as order_item_key,
    l_orderkey as order_key,
    l_partkey as part_key,
    l_linenumber as line_number,
    l_quantity as quantity,
    l_extendedprice as extended_price,
    l_discount as discount_percentage,
    l_tax as tax_rate
from
    {{ source('tpch', 'lineitem') }}
```

This model:
- Uses `dbt_utils.generate_surrogate_key()` to create a unique identifier for each order item
- Selects and renames columns from the lineitem table
- Follows the same naming convention as the orders model

## Step 4: Run Your Staging Models

Now let's execute these models:

```bash
dbt run --select staging
```

This command runs all models in the staging directory.

## Step 5: Test Your Source Data

Run the tests defined in the sources file:

```bash
dbt test --select source:tpch
```

This verifies that our source data passes the quality tests we defined.

## Step 6: View Your Staging Models

Run the following commands to see the SQL generated for your models:

```bash
dbt compile --select staging
```

You can find the compiled SQL in the `target/compiled/snowflake_workshop/models/staging/` directory.

To explore the resulting tables and views in Snowflake:

```sql
-- In Snowflake
USE DATABASE dbt_db;
USE SCHEMA dbt_schema;

-- View the orders staging model
SELECT * FROM stg_tpch_orders LIMIT 10;

-- View the line items staging model
SELECT * FROM stg_tpch_line_items LIMIT 10;
```

## Summary

In this section, we:
- Defined source tables from Snowflake's sample data
- Created staging models that clean and standardize the raw data
- Added basic data quality tests
- Executed and verified our staging models

The staging layer forms the foundation of our data transformation pipeline. It standardizes column names and formats, making downstream transformations simpler and more consistent. By separating this layer from more complex transformations, we make our dbt project more maintainable and easier to understand.

Next, we'll create reusable dbt macros to avoid duplicating SQL logic.

## Resources

- [dbt Sources Documentation](https://docs.getdbt.com/docs/building-a-dbt-project/using-sources)
- [dbt Staging Patterns](https://docs.getdbt.com/best-practices/how-we-structure/1-staging)
- [dbt Testing](https://docs.getdbt.com/docs/building-a-dbt-project/tests)
