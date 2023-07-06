from enum import Enum
from sdk.utils.exceptions import UnknownCommandError


class Commands(Enum):
    GenerateTextCommand = "GenerateTextCommand"


def get_commands_help():
    return {
        "overview": "Sends text to the user. You need to provide the exact text that will be sent to the user.",
        "commands": [
            {
                "command": {
                    "command_name": "GenerateTextCommand",
                    "args": {'message': "text message to be shown", "require_result_summary": False},
                },
                "command_description": "Generate a simple text command to be shown in the chat app"
            }
        ]
    }


def handle_command(command):
    if command["command_name"] == Commands.GenerateTextCommand.name:
        return {
            "message": command["args"]["message"]
        }

    else:
        raise UnknownCommandError(f"Unknown command: {command['command_name']}")
