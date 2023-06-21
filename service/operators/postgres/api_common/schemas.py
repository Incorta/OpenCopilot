from configs.env import db_name, db_user, db_password, db_host, db_port
from utils import logger
import psycopg2

def get_schemas():
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )

    # Create a cursor object
    cursor = conn.cursor()

    # Execute query to get all schemas
    cursor.execute(""" SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'; """)

    # Fetch all rows
    schemas = cursor.fetchall()
    schemas_names = []
    # Print the list of schemas
    for schema in schemas:
        print(schema[1])
        schemas_names.append(schema[1])

    # Close cursor and connection
    cursor.close()
    conn.close()

    return schemas_names

def get_schema_tables(schema_name, include_columns=False):
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )

    # Create a cursor object
    cursor = conn.cursor()

    # Execute query to get all schemas
    cursor.execute(" SELECT table_name FROM information_schema.tables WHERE table_schema = '" + schema_name + "'; ")

    # Fetch all rows
    tables = cursor.fetchall()
    tables_names = []
    # Print the list of schemas
    for table in tables:
        tables_names.append(table[0])

    # Close cursor and connection
    cursor.close()
    conn.close()

    return tables_names

def get_table_columns(schema_name, table_name):
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )

    # Create a cursor object
    cursor = conn.cursor()

    # Execute query to get all schemas
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = '" + schema_name + "' AND table_name = '" + table_name + "';")

    # Fetch all rows
    columns = cursor.fetchall()
    columns_names = []
    # Print the list of schemas
    for column in columns:
        columns_names.append(column)

    # Close cursor and connection
    cursor.close()
    conn.close()
    return columns_names
