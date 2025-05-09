# Setting Up Your dbt Project

Now that our Snowflake environment is ready, let's set up our dbt project to start transforming data.

## Step 1: Install dbt

First, install dbt with the Snowflake adapter:

```bash
pip install dbt-snowflake
```

## Step 2: Initialize a dbt Project

Create a new dbt project:

```bash
# Navigate to your project directory
cd /path/to/your/project

# Initialize a new dbt project
dbt init snowflake_workshop
```

This command creates a new dbt project with a standard directory structure. Let's navigate into it:

```bash
cd snowflake_workshop
```

## Step 3: Configure dbt Profile

Create or edit `~/.dbt/profiles.yml` to include your Snowflake connection details:

```yaml
snowflake_workshop:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: [your_account_id]
      user: [your_username]
      password: [your_password]
      role: dbt_role
      database: dbt_db
      warehouse: dbt_wh
      schema: dbt_schema
      threads: 4
```

Replace the placeholders with your actual Snowflake credentials:
- `[your_account_id]`: Your Snowflake account identifier (e.g., xy12345.us-east-1)
- `[your_username]`: Your Snowflake username
- `[your_password]`: Your Snowflake password

## Step 4: Configure dbt Project

Edit the `dbt_project.yml` file in your project root directory:

```yaml
name: 'snowflake_workshop'
version: '1.0.0'
config-version: 2

profile: 'snowflake_workshop'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  snowflake_workshop:
    staging:
      materialized: view
      snowflake_warehouse: dbt_wh
    marts:
      materialized: table
      snowflake_warehouse: dbt_wh
```

This configuration specifies:
- Project name and version
- The profile to use for connecting to Snowflake
- Directory paths for models, tests, macros, etc.
- Materialization strategies for different model types:
  - Staging models will be created as views
  - Mart models will be created as tables

## Step 5: Install Required Packages

Create a `packages.yml` file in your project root directory:

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.0.0
```

Then install the packages:

```bash
dbt deps
```

## Step 6: Test Your Connection

Verify that dbt can connect to your Snowflake account:

```bash
dbt debug
```

If everything is configured correctly, you should see output indicating that the connection to Snowflake was successful.

## Summary

In this section, we:
- Installed dbt with the Snowflake adapter
- Initialized a new dbt project
- Configured the dbt profile for connecting to Snowflake
- Set up the dbt project configuration with materialization strategies
- Added necessary dbt packages
- Tested the connection to Snowflake

Our dbt project is now ready for development. We've established the connection to Snowflake and configured how our models will be materialized.

Next, we'll create source and staging models to start transforming our data.

## Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [dbt-utils Package](https://github.com/dbt-labs/dbt-utils)
