from operators.postgres.api_helpers.connect_sql import Database
from sdk.utils import logger

db_object = Database()


def get_schemas():
    logger.system_message("Executing query to retrieve all schemas")

    # Execute query to get all schemas
    get_all_schemas_query = "SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"
    schemas = db_object.execute_query(get_all_schemas_query)
    schemas_names = []
    for schema in schemas:
        schemas_names.append(schema[1])
    return schemas_names


def get_schema_tables(schema_name):
    logger.system_message("Executing query to retrieve schema tables")

    # Execute query to get all schema tables
    get_tables_from_schema_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema_name}';"
    tables = db_object.execute_query(get_tables_from_schema_query)
    tables_names = []
    for table in tables:
        tables_names.append(table[0])
    return tables_names


def get_table_columns(schema_name, table_name):
    logger.system_message("Executing query to retrieve table columns")

    # Execute query to get all table columns
    get_all_columns_query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = '{schema_name}' AND table_name = '{table_name}';"
    columns = db_object.execute_query(get_all_columns_query)
    columns_names = []
    for column in columns:
        columns_names.append(column)
    return columns_names
