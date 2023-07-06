from enum import Enum
from operators.postgres.memory import metadata_context_retriever
from opencopilot.utils.exceptions import UnknownCommandError


class Commands(Enum):
    GetRelevantTable = "GetRelevantTable"


def get_commands_help():
    return {
        "overview": "I'm MetaDataOp, I can get you the table and columns that's most relevant to the user query.",
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
        return metadata_context_retriever.get_top_relevant_tables(1, command["args"]["query"])
    else:
        raise UnknownCommandError(f"Unknown command: {command['command_name']}")
