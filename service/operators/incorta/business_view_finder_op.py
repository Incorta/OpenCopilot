from enum import Enum

from operators.incorta.api_common import schemas
from operators.incorta.memory import metadata_context_retriever
from utils.exceptions import UnknownCommandError


class Commands(Enum):
    GetRelevantView = "GetRelevantView"
    ListRelevantViews = "ListRelevantViews"
    ListRelevantColumnsInViews = "ListRelevantColumnsInViews"
    SelectMostRelevantView = "SelectMostRelevantView"


def get_commands_help():
    return {
        "overview": "I'm BusinessViewFinderOp, I can get you the business view that's most relevant to the user query.",
        "commands": [
            {
                "command": {
                    "command_name": "GetRelevantView",
                    "args": {"query": "Query to search for the most relevant view", "require_result_summary": False},
                },
                "command_description": "Given query, search the available views, to find the most relevant view. "
                                       "That contains all the required field",
            }
        ],
        "expected_sub_tasks_count": 1
    }


def handle_command(command):
    if command["command_name"] == Commands.GetRelevantView.name:
        return metadata_context_retriever.get_top_relevant_view(1, command["args"]["query"])

    elif command["command_name"] == Commands.ListRelevantViews.name:
        return metadata_context_retriever.get_top_relevant_schemas(5, command["args"]["query"])

    elif command["command_name"] == Commands.ListRelevantColumnsInViews.name:
        return schemas.get_schema_views(command["args"]["schema_name"])

    elif command["command_name"] == Commands.SelectMostRelevantView.name:
        return schemas.get_business_view_columns(command["args"]["schema_name"], command["args"]["table_name"])

    else:
        raise UnknownCommandError(f"Unknown command: {command['command_name']}")
