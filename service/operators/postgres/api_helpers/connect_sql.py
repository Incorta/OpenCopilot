import json
import psycopg
import urllib.parse
from configs import env
import datetime


def get_db_args():
    return env.db_name, env.db_user, env.db_password, env.db_host


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


def handle_postgres_datetime(query_results):
    for i in range(len(query_results)):
        query_results[i] = list(query_results[i])
        for j in range(len(query_results[i])):
            if type(query_results[i][j]) is datetime.datetime:
                date_string = query_results[i][j].strftime("%Y-%m-%d %H:%M:%S")
                query_results[i][j] = date_string
        query_results[i] = tuple(query_results[i])
    return query_results


def run_sql_query(sql_query):
    db_name, db_user, db_password, db_host = get_db_args()
    encoded_password = urllib.parse.quote(db_password)

    postgres_url = f"postgresql://{db_user}:{encoded_password}@{db_host}/{db_name}"
    with psycopg.connect(postgres_url) as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cursor:
            cursor.execute(sql_query)
            results = cursor.fetchall()
            results = handle_postgres_datetime(list(results))
            return results
