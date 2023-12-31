from enum import Enum
from opencopilot.utils.exceptions import UnknownCommandError


class Commands(Enum):
    GenerateTextCommand = "GenerateTextCommand"


def get_commands_help():
    return {
        "commands": [
            {
                "command": {
                    "command_name": "GenerateTextCommand",
                    "args": {'message': "the exact text that will be sent to the user."},
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
