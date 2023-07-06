from enum import Enum
from operators.postgres.api_helpers import connect_sql
from opencopilot.utils.exceptions import UnknownCommandError


class Commands(Enum):
    getQuery = "getQuery"


def get_commands_help():
    return {
        "overview": """ Creates a sql query and executes it on SQL DB. The queries would be on data and not metadata. """
        ,
        "commands": [
            {
                "command": {
                    "command_name": "getQuery",
                    "args": {
                        "relevant_table": "The relevant table name",
                        "column_names_list": "A list of all column names from view_columns field for the relevant table",
                        "query": "A PostgreSQL 10.6 query that includes table and column names. Create a list of column names from view_columns list, then choose appropriate column names from this list to construct the query. You should never use a column name in the query that does not exist in this list. Add semicolon at the end. Make sure the constructed query is supported by most databases. Due to certain restrictions, you can only return 10 rows at a time. Therefore, try to use SQL queries that provide aggregated data and insights rather than individual rows whenever possible. Always include a LIMIT clause to ensure that only 10 rows are returned. ",
                        "require_result_summary": False
                    },
                },
                "command_description": "Creates a SQL query to be executed on SQL database. You must first list all possible column names in column_names_list, then choose from this list column names to be used in the query. Never use a column name in the query other than column names in column_names_list."
            }
        ]
    }


def handle_command(command):
    if command["command_name"] == Commands.getQuery.name:
        return connect_sql.get_query_result(command["args"]["query"])
    else:
        raise UnknownCommandError(f"Unknown command: {command['command_name']}")
