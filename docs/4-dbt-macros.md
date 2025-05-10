# Implementing dbt Macros

In this section, we'll create reusable SQL macros to avoid duplicating code across our models.

## What are dbt Macros?

Macros in dbt are similar to functions in other programming languages. They allow you to:
- Define reusable SQL logic
- Accept parameters to make the code more flexible
- Implement DRY (Don't Repeat Yourself) principles in your SQL code

## Step 1: Create a Pricing Macro

Let's create a macro to calculate discounted amounts. Create a file called `macros/pricing.sql`:

```sql
{% macro discounted_amount(extended_price, discount_percentage, scale=2) %}
    (-1 * {{extended_price}} * {{discount_percentage}})::decimal(16, {{ scale }})
{% endmacro %}
```

This macro:
- Takes two required parameters: `extended_price` and `discount_percentage`
- Takes an optional parameter `scale` with a default value of 2
- Returns the discounted amount as a decimal with the specified scale
- The `-1` multiplier makes the discount a negative value (a reduction in price)

## Step 2: Understanding Macro Parameters

Our macro accepts three parameters:
1. `extended_price`: The original price before discount
2. `discount_percentage`: The discount percentage (as a decimal, e.g., 0.15 for 15%)
3. `scale`: Optional parameter to specify decimal precision (defaults to 2)

## Step 3: Using the Macro in Models

In subsequent models, we can use this macro as follows:

```sql
select
    order_item_key,
    extended_price,
    {{ discounted_amount('extended_price', 'discount_percentage') }} as item_discount_amount
from
    {{ ref('stg_tpch_line_items') }}
```

This will compile to:

```sql
select
    order_item_key,
    extended_price,
    (-1 * extended_price * discount_percentage)::decimal(16, 2) as item_discount_amount
from
    "dbt_db"."dbt_schema"."stg_tpch_line_items"
```

## Step 4: Testing Your Macro

Let's create a simple test model to verify our macro works correctly. Create `models/staging/test_macro.sql`:

```sql
-- This is just for testing, we can delete it later
select
    order_item_key,
    extended_price,
    discount_percentage,
    {{ discounted_amount('extended_price', 'discount_percentage') }} as item_discount_amount,
    {{ discounted_amount('extended_price', 'discount_percentage', 4) }} as item_discount_amount_4dp
from
    {{ ref('stg_tpch_line_items') }}
limit 10
```

Run this model to see the macro in action:

```bash
dbt run --select staging.test_macro
```

Check the results in Snowflake:

```sql
-- In Snowflake
SELECT * FROM dbt_db.dbt_schema.test_macro;
```

## Step 5: Creating Additional Macros (Optional)

You can create more macros for other common calculations. For example, a macro to calculate the tax amount:

```sql
{% macro tax_amount(extended_price, tax_rate, scale=2) %}
    ({{extended_price}} * {{tax_rate}})::decimal(16, {{ scale }})
{% endmacro %}
```

## Step 6: Organizing Macros

As your project grows, consider organizing macros by category:

```
macros/
├── pricing/
│   ├── discounted_amount.sql
│   └── tax_amount.sql
├── date/
│   ├── fiscal_year.sql
│   └── is_weekend.sql
└── string/
    └── clean_string.sql
```

With this structure, you would need to update your macro imports in models:

```sql
select
    {{ pricing.discounted_amount('extended_price', 'discount_percentage') }} as discount
from
    {{ ref('stg_tpch_line_items') }}
```

## Summary

In this section, we:
- Created a reusable macro for calculating discounted amounts
- Learned how to define parameters and return values in macros
- Tested the macro with a simple model
- Discussed strategies for organizing macros in larger projects

Macros are a powerful feature in dbt that help maintain consistent business logic across your models. By centralizing calculations in macros, you ensure that changes to business logic only need to be made in one place, reducing the risk of inconsistencies in your data models.

Next, we'll create transformation models that use our staging models and macros to build more complex data structures.

## Resources

- [dbt Macros Documentation](https://docs.getdbt.com/docs/building-a-dbt-project/jinja-macros)
- [Jinja Template Documentation](https://jinja.palletsprojects.com/en/3.0.x/templates/)
