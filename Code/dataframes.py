import pandas as pd

from database import engine

from queries import \
    get_query_body, get_query_last_body, \
    get_query_meals, get_query_nutrition, \
    get_query_exercises, get_query_workout, get_query_last_workout, \
    get_query_exists, get_query_insert, get_query_update, get_query_delete



# Body
def get_df_body(date_min, date_max):
    df_body = (
        pd.read_sql(
            get_query_body(date_min, date_max), 
            engine, 
        )
        .set_index('Date')
    )
    return(df_body)

def get_s_last_body(date):

    s_last_body = (
        pd.read_sql(
            get_query_last_body(date), 
            engine, 
        )
        .iloc[-1]
    )
    return(s_last_body)

# Nutrition
def get_df_meals():
    df_meals = (
        pd.read_sql(
            get_query_meals(), 
            engine, 
        )
    )
    return(df_meals)

def get_df_nutrition(level, genre, date_min, date_max):
    df_nutrition = (
        pd.read_sql(
            get_query_nutrition(level, genre, date_min, date_max), 
            engine, 
        )
        .set_index({'Date': ['Date'], 'Meal': ['Date', 'Meal'], 'Aliment': ['Date', 'Meal', 'Aliment']}.get(level))
    )
    return(df_nutrition)

# Workout
def get_df_exercises():
    df_workout = (
        pd.read_sql(
            get_query_exercises(), 
            engine, 
        )
    )
    return(df_workout)

def get_df_workout(date_min, date_max):
    df_workout = (
        pd.read_sql(
            get_query_workout(date_min, date_max), 
            engine, 
        )
        .set_index('Date')
    )
    return(df_workout)

def get_df_last_workout(date):

    df_last_workout = (
        pd.read_sql(
            get_query_last_workout(date), 
            engine, 
        )
        
        .drop_duplicates(subset=['Pattern', 'Resistance'], keep='last')
        .set_index(['Pattern', 'Resistance'])
    )
    return(df_last_workout)

# Edit
def execute_query(query):
    connection = engine.connect()
    connection.execute(query)
    connection.close()
def get_scalar_from_query(query):
    connection = engine.connect()
    scalar = connection.execute(query).scalar()
    connection.close()
    return(scalar)

def insert_row(table, row):

    row = {key: value for key, value in row.items() if value is not None}

    query_insert = get_query_insert(table, row)
    execute_query(query_insert)
def upsert_row(table, row):

    row = {key: value for key, value in row.items() if value is not None}

    query_exists = get_query_exists(table, row)
    if not get_scalar_from_query(query_exists):
        query_insert = get_query_insert(table, row)
        execute_query(query_insert)
    else:
        query_update = get_query_update(table, row)
        execute_query(query_update)
def delete_row(table, row):

    row = {key: value for key, value in row.items() if value is not None}

    query_exists = get_query_exists(table, row)
    if get_scalar_from_query(query_exists):
        query_delete = get_query_delete(table, row)
        execute_query(query_delete)
