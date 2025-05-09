# Setting Up Your Snowflake Environment

Before we can start transforming data with dbt, we need to create and configure a Snowflake environment. This will serve as our data warehouse where all transformations will take place.

## Step 1: Create a Snowflake Account

If you don't already have a Snowflake account, you can sign up for a free trial at [snowflake.com](https://www.snowflake.com).

## Step 2: Log in to Snowflake and Open a Worksheet

After logging in to your Snowflake account, navigate to the Worksheets section to execute SQL commands.

## Step 3: Set Up the Required Snowflake Objects

Run the following SQL commands to create the necessary Snowflake objects:

```sql
-- Use the ACCOUNTADMIN role for creating accounts
USE ROLE ACCOUNTADMIN;

-- Create a warehouse for our dbt transformations
CREATE WAREHOUSE dbt_wh WITH WAREHOUSE_SIZE='X-SMALL';

-- Create a database for our dbt models
CREATE DATABASE IF NOT EXISTS dbt_db;

-- Create a custom role for dbt
CREATE ROLE IF NOT EXISTS dbt_role;

-- Verify the grants on our warehouse
SHOW GRANTS ON WAREHOUSE dbt_wh;

-- Grant the dbt role to your user
-- Replace 'your_username' with your actual Snowflake username
GRANT ROLE dbt_role TO USER your_username;

-- Grant usage permissions on the warehouse to our role
GRANT USAGE ON WAREHOUSE dbt_wh TO ROLE dbt_role;

-- Grant all privileges on the database to our role
GRANT ALL ON DATABASE dbt_db TO ROLE dbt_role;

-- Switch to the dbt role for subsequent operations
USE ROLE dbt_role;

-- Create a schema in our database for dbt models
CREATE SCHEMA IF NOT EXISTS dbt_db.dbt_schema;
```

## Step 4: Verify Your Setup

To ensure everything is set up correctly, run the following commands:

```sql
-- Check that you can use the warehouse
USE WAREHOUSE dbt_wh;

-- Check that you can access the database and schema
USE DATABASE dbt_db;
USE SCHEMA dbt_schema;

-- Verify access to the sample data we'll be using
SELECT COUNT(*) FROM snowflake_sample_data.tpch_sf1.orders;
SELECT COUNT(*) FROM snowflake_sample_data.tpch_sf1.lineitem;
```

If these commands execute without errors, your Snowflake environment is correctly set up!

## Cleanup (Optional)

If you need to clean up your environment and start over, you can use the following commands:

```sql
-- Switch back to ACCOUNTADMIN role
USE ROLE ACCOUNTADMIN;

-- Drop the objects we created
DROP WAREHOUSE IF EXISTS dbt_wh;
DROP DATABASE IF EXISTS dbt_db;
DROP ROLE IF EXISTS dbt_role;
```

## Summary

In this section, we:
- Created a dedicated warehouse for our dbt transformations
- Set up a database and schema for our dbt models
- Created a custom role with appropriate permissions
- Verified access to the sample data we'll be using

The Snowflake environment is now ready for our dbt project. This separation of resources helps maintain a clean environment and makes it easier to manage permissions and resource usage.

Next, we'll set up our dbt project structure.

## Resources

- [Snowflake Documentation](https://docs.snowflake.com/)
- [Snowflake Sample Data](https://docs.snowflake.com/en/user-guide/sample-data)
