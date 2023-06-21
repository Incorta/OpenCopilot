from enum import Enum

from operators.postgres.api_common import schemas
from operators.postgres.memory import metadata_context_retriever
from utils.exceptions import UnknownCommandError


class Commands(Enum):
    GetRelevantTable = "GetRelevantTable"
    ListRelevantTables = "ListRelevantTables"
    ListRelevantColumnsInTables = "ListRelevantColumnsInTables"
    SelectMostRelevantTable = "SelectMostRelevantTable"


def get_commands_help():
    return {
        "overview": "I'm TableFinderOp, I can get you the table and columns that's most relevant to the user query.",
        "commands": [
            {
                "command": {
                    "command_name": "GetRelevantTable",
                    "args": {"query": "Query to search for the most relevant table", "require_result_summary": False},
                },
                "command_description": "Given query, search the available tables, to find the most relevant table. "
                                       "That contains all the required fields",
            }
        ],
        "expected_sub_tasks_count": 1
    }


def handle_command(command):
    if command["command_name"] == Commands.GetRelevantTable.name:
        return metadata_context_retriever.get_top_relevant_table(1, command["args"]["query"])

    elif command["command_name"] == Commands.ListRelevantTables.name:
        return metadata_context_retriever.get_top_relevant_table(5, command["args"]["query"])

    elif command["command_name"] == Commands.ListRelevantColumnsInTables.name:
        return schemas.get_schema_tables(command["args"]["schema_name"])

    elif command["command_name"] == Commands.SelectMostRelevantTable.name:
        return schemas.get_table_columns(command["args"]["schema_name"], command["args"]["table_name"])

    else:
        raise UnknownCommandError(f"Unknown command: {command['command_name']}")
