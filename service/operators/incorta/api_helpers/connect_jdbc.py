import json
import psycopg
import urllib.parse
from configs import env
import datetime
from utils import logger
from operators.incorta.api_helpers import post


def get_db_args():
    return env.db_name, env.db_user, env.db_password


def format_sql_result(results, columns):
    records = []
    for row in results:
        record = {}
        for i, value in enumerate(row):
            # Check if value is a datetime object
            if isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')  # Convert to string
            record[columns[i]] = value  # Map column name to value
        records.append(record)

    return json.dumps(records)


def run_sql_query_jdbc(sql_query):
    logger.system_message("Getting schemas from incorta")
    url = f'{env.incorta_url}/incorta/api/v2/configs/sqlConnection'

    jdbc_host = post.run_plain_response(url, env.incorta_api_access_token)
    print("JDBC Host:" + jdbc_host)

    jdbc_database, jdbc_user, jdbc_password = get_db_args()
    encoded_password = urllib.parse.quote(jdbc_password)

    postgres_url = f"postgresql://{jdbc_user}:{encoded_password}@{jdbc_host}/{jdbc_database}"

    # Connect to an existing database
    with psycopg.connect(postgres_url) as conn:
        conn.adapters.register_loader("date", psycopg.types.string.TextLoader)
        conn.adapters.register_loader("integer", psycopg.types.string.TextLoader)
        conn.adapters.register_loader("numeric", psycopg.types.string.TextLoader)
        conn.adapters.register_loader("bigint", psycopg.types.string.TextLoader)
        conn.adapters.register_loader("smallint", psycopg.types.string.TextLoader)

        # Open a cursor to perform database operations
        with conn.cursor() as cursor:
            cursor.execute(sql_query)
            results = cursor.fetchall()
            return results
            # columns = [desc[0] for desc in cursor.description]
            # return format_sql_result(results, columns)
