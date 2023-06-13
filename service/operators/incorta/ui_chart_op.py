from enum import Enum

from utils.exceptions import UnknownCommandError


class Commands(Enum):
    GenerateChartJson = "GenerateChartJson"


def get_commands_help():
    return {
        "overview": "I'm the UiChartOp, I can draw charts and display it for you, given that I have sample data in json format from the QueryOp",
        "commands": [
            {
                "command": {
                    "command_name": "GenerateChartJson",
                    "args": {'generated_json': "A string containing a valid plotly json object with correct double quotes. You must encode the plotly JSON as string first then put it here",
                             "require_result_summary": False},
                },
                "command_description": "Generate a ready to render Plotly json string that has a suitable chart for the data, include the layout"
            }
        ]
    }


def handle_command(command):
    if command["command_name"] == Commands.GenerateChartJson.name:
        return command["args"]["generated_json"]

    else:
        raise UnknownCommandError(f"Unknown command: {command['command_name']}")
