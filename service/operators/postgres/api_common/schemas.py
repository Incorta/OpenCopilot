from configs.env import db_name, db_user, db_password, db_host, db_port
from utils import logger
import psycopg2


def get_db_connection(sql_query):
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )

    # Create a cursor object
    cursor = conn.cursor()
    cursor.execute(sql_query)

    # Get result from database
    result = cursor.fetchall()

    # Close cursor and connection
    cursor.close()
    conn.close()
    return result


def get_schemas():
    logger.system_message("Executing query to retrieve all schemas")

    # Execute query to get all schemas
    get_all_schemas_query = "SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"
    schemas = get_db_connection(get_all_schemas_query)
    schemas_names = []
    for schema in schemas:
        schemas_names.append(schema[1])
    return schemas_names


def get_schema_tables(schema_name):
    logger.system_message("Executing query to retrieve schema tables")

    # Execute query to get all schemas
    get_tables_from_schema_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema_name}';"
    tables = get_db_connection(get_tables_from_schema_query)
    tables_names = []
    for table in tables:
        tables_names.append(table[0])
    return tables_names


def get_table_columns(schema_name, table_name):
    logger.system_message("Executing query to retrieve table columns")

    # Execute query to get all schemas
    get_all_schemas_query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = '{schema_name}' AND table_name = '{table_name}';"
    columns = get_db_connection(get_all_schemas_query)
    columns_names = []
    for column in columns:
        columns_names.append(column)
    return columns_names
