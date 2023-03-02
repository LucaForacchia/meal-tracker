# MealTracker Backend

version 0.1.0

# How to use

## Setup

Please use python 3.7 and install dependencies using pip3

    > pip3 install -r requirements.txt

## Launch the server

Start the server from command line with:

    > python src/main.py

## Configuration

Software configuration is driven by env variables:

| Variable | Meaning | Default/Allowed values |
|----------|---------|----------------|
| db_type | Db type to be used | sqlite (default); mysql |
| meal_db_path | Configure sqlite db path | /tmp/meal-tracker/meals.db |
| db_host | Db host for mysql | - |
| db_name | Db name for mysql | - |
| db_user | Db user for mysql | - |
| db_pass | Db pass for mysql | - |