import configs
import datetime
import psycopg2


class Database:
    def __init__(self):
        self.dbname = configs.db_name
        self.user = configs.db_user
        self.password = configs.db_password
        self.host = configs.db_host
        self.port = configs.db_port

    def get_connection(self):
        conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        return conn

    def execute_query(self, query):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows


def handle_postgres_datetime(query_results):
    for i in range(len(query_results)):
        query_results[i] = list(query_results[i])
        for j in range(len(query_results[i])):
            if type(query_results[i][j]) is datetime.datetime:
                date_string = query_results[i][j].strftime("%Y-%m-%d %H:%M:%S")
                query_results[i][j] = date_string
        query_results[i] = tuple(query_results[i])
    return query_results


def get_query_result(sql_query):
    db_object = Database()
    result = db_object.execute_query(sql_query)
    formatted_result = handle_postgres_datetime(list(result))
    return formatted_result
