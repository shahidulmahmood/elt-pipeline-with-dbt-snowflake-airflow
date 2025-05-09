# Building Transformation Models

Now that we have our staging models and macros set up, we can build more complex transformation models. These models will form the analytical layer of our data pipeline.

## Understanding the Transformation Layer

Our transformation layer will consist of:

1. **Intermediate models** - These models join and prepare data from staging tables
2. **Fact tables** - These models represent business processes and contain measures and metrics

## Step 1: Create an Intermediate Model for Order Items

Create a file called `models/marts/int_order_items.sql`:

```sql
select
    line_item.order_item_key,
    line_item.part_key,
    line_item.line_number,
    line_item.extended_price,
    orders.order_key,
    orders.customer_key,
    orders.order_date,
    {{ discounted_amount('line_item.extended_price', 'line_item.discount_percentage') }} as item_discount_amount
from
    {{ ref('stg_tpch_orders') }} as orders
join
    {{ ref('stg_tpch_line_items') }} as line_item
        on orders.order_key = line_item.order_key
order by
    orders.order_date
```

This intermediate model:
- Joins the staging orders and line items tables
- Uses our `discounted_amount` macro to calculate the discount
- Creates a combined dataset with information from both tables

## Step 2: Create a Summary Intermediate Model

Create a file called `models/marts/int_order_items_summary.sql`:

```sql
select 
    order_key,
    sum(extended_price) as gross_item_sales_amount,
    sum(item_discount_amount) as item_discount_amount
from
    {{ ref('int_order_items') }}
group by
    order_key
```

This model:
- Aggregates data from the previous intermediate model
- Calculates summary metrics by order
- Creates a consolidated view of sales and discounts per order

## Step 3: Create a Fact Table for Orders

Create a file called `models/marts/fct_orders.sql`:

```sql
select
    orders.*,
    order_item_summary.gross_item_sales_amount,
    order_item_summary.item_discount_amount
from
    {{ref('stg_tpch_orders')}} as orders
join
    {{ref('int_order_items_summary')}} as order_item_summary
        on orders.order_key = order_item_summary.order_key
order by order_date
```

This fact table:
- Combines order information with aggregated metrics
- Provides a comprehensive view of each order with its associated financial metrics
- Represents our final analytical model

## Step 4: Run Your Models

Execute the models in order:

```bash
# Run the intermediate models first
dbt run --select marts.int_order_items marts.int_order_items_summary

# Then run the fact model
dbt run --select marts.fct_orders
```

Alternatively, run all models with dependencies resolved automatically:

```bash
dbt run --select marts.fct_orders+
```

## Step 5: Explore Your Models in Snowflake

Connect to Snowflake and explore your new models:

```sql
-- In Snowflake
USE DATABASE dbt_db;
USE SCHEMA dbt_schema;

-- View the intermediate model
SELECT * FROM int_order_items LIMIT 10;

-- View the summary model
SELECT * FROM int_order_items_summary LIMIT 10;

-- View the fact table
SELECT * FROM fct_orders LIMIT 10;

-- Run some analysis queries
SELECT 
    DATE_TRUNC('MONTH', order_date) as month,
    SUM(gross_item_sales_amount) as gross_sales,
    SUM(item_discount_amount) as total_discounts,
    SUM(gross_item_sales_amount) + SUM(item_discount_amount) as net_sales
FROM 
    fct_orders
GROUP BY 
    month
ORDER BY 
    month;
```

## Step 6: Visualize Your Transformation DAG

Generate a DAG (Directed Acyclic Graph) of your models:

```bash
dbt docs generate
dbt docs serve
```

This opens a browser window where you can explore the relationships between your models.

## Summary

In this section, we:
- Created intermediate models that join and prepare data
- Built a summary model that aggregates metrics
- Created a fact table for comprehensive order analysis
- Ran and explored our transformation models
- Visualized the dependencies between our models

This modular approach to data transformation provides several benefits:
1. **Reusability**: Intermediate models can be reused across multiple fact tables
2. **Maintainability**: Each model has a clear, specific purpose
3. **Performance**: Intermediate tables can be materialized for faster downstream queries
4. **Clarity**: The data pipeline is easier to understand and document

Next, we'll add data quality tests to ensure our transformations are working correctly.

## Resources

- [dbt Modeling Documentation](https://docs.getdbt.com/docs/building-a-dbt-project/building-models)
- [dbt Materializations](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/materializations)
- [Kimball Dimensional Modeling](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
