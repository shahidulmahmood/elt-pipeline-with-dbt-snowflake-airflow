# Adding Data Tests

Testing is a critical part of any data pipeline. In this section, we'll implement both generic and singular tests to ensure our data meets quality standards.

## Understanding dbt Tests

dbt supports two types of tests:

1. **Generic tests** - Predefined tests like uniqueness and referential integrity
2. **Singular tests** - Custom SQL queries that should return zero rows when the test passes

## Step 1: Add Generic Tests to Your Models

Create a file called `models/marts/generic_tests.yml` to define tests for your fact table:

```yaml
models:
  - name: fct_orders
    columns:
      - name: order_key
        tests:
          - unique
          - not_null
          - relationships:
              to: ref('stg_tpch_orders')
              field: order_key
              severity: warn
      - name: status_code
        tests:
          - accepted_values:
              values: ['P', 'O', 'F']
```

These tests verify that:
- `order_key` is unique and not null
- `order_key` exists in the staging orders table (referential integrity)
- `status_code` only contains the accepted values 'P', 'O', or 'F'

Note that the relationship test has a `severity` of `warn`, which means the test will warn but not fail the pipeline if it doesn't pass.

## Step 2: Create a Singular Test for Discounts

Create a file called `tests/fct_orders_discount.sql`:

```sql
select
    *
from
    {{ref('fct_orders')}}
where
    item_discount_amount > 0
```

This test will fail if there are any orders with positive discount amounts, which would be incorrect since discounts should reduce the price (negative values).

## Step 3: Create a Date Validation Test

Create a file called `tests/fct_orders_date_valid.sql`:

```sql
select
    *
from
    {{ref('fct_orders')}}
where
    date(order_date) > CURRENT_DATE()
    or date(order_date) < date('1990-01-01')
```

This test ensures that all order dates are within a reasonable range (not in the future and not before 1990).

## Step 4: Run Your Tests

Execute all tests:

```bash
dbt test
```

Or run specific tests:

```bash
# Run generic tests on the fact table
dbt test --select fct_orders

# Run singular tests
dbt test --select test_type:singular
```

## Step 5: Customize Test Behavior

You can customize test behavior by adding configuration:

```yaml
models:
  - name: fct_orders
    columns:
      - name: order_key
        tests:
          - unique:
              severity: error  # Will cause the pipeline to fail
          - not_null:
              where: "status_code != 'F'"  # Only test non-finalized orders
```

## Step 6: Create a Test Coverage Report

Create a file called `analyses/test_coverage.sql`:

```sql
with models as (
    select 
        table_schema as schema_name,
        table_name as model_name,
        column_name
    from 
        information_schema.columns
    where 
        table_schema = 'dbt_schema'
),

tests as (
    select 
        'unique' as test_name,
        table_name as model_name,
        column_name
    from 
        information_schema.table_constraints
    where 
        constraint_type = 'UNIQUE'
        and table_schema = 'dbt_schema'
)

select 
    models.schema_name,
    models.model_name,
    models.column_name,
    case when tests.test_name is not null then 'Yes' else 'No' end as has_test
from 
    models
left join
    tests
    on models.model_name = tests.model_name
    and models.column_name = tests.column_name
order by
    models.model_name,
    models.column_name;
```

## Step 7: Interpreting Test Results

When you run your tests, dbt will provide output similar to:

```
Running 5 tests
 
test unique_fct_orders_order_key................................. [PASS in 0.28s]
test not_null_fct_orders_order_key............................... [PASS in 0.23s]
test relationships_fct_orders_order_key_stg_tpch_orders_order_key [PASS in 0.31s]
test accepted_values_fct_orders_status_code...................... [PASS in 0.24s]
test fct_orders_discount......................................... [PASS in 0.25s]
test fct_orders_date_valid....................................... [PASS in 0.22s]

Completed successfully
```

If a test fails, you'll see details about the failure and instructions on how to view the failed records.

## Summary

In this section, we:
- Added generic tests to validate key data quality assumptions
- Created custom singular tests for business logic validation
- Learned how to run and interpret test results
- Created a test coverage analysis

Testing is a critical part of any data pipeline:
1. It provides confidence in the quality of your data
2. It helps catch issues early in the pipeline
3. It documents data assumptions and business rules
4. It ensures your transformations are working as expected

By implementing a comprehensive testing strategy, we've increased the reliability of our data pipeline and clearly documented our data quality expectations.

Next, we'll deploy our dbt pipeline with Apache Airflow for automated scheduling and monitoring.

## Resources

- [dbt Testing Documentation](https://docs.getdbt.com/docs/building-a-dbt-project/tests)
- [dbt Test Configurations](https://docs.getdbt.com/reference/resource-configs/tests)
- [Data Quality Testing Best Practices](https://docs.getdbt.com/best-practices/data-quality-testing)