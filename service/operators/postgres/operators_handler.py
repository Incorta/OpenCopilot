from operators.postgres import query_op, metadata_op, ui_text_op

op_functions = {
    "MetaDataOp": {
        "get_commands_help": metadata_op.get_commands_help,
        "handle_command": lambda command: metadata_op.handle_command(command),
        "file_name": "metadata_op",
        "description": "All queries must be against a single table, this operator can help you find the most relevant table.",
        "operator_name": "SQL Metadata Helper"
    },
    "QueryOp": {
        "get_commands_help": query_op.get_commands_help,
        "handle_command": lambda command: query_op.handle_command(command),
        "file_name": "query_op",
        "description": "This operator requires input from the MetaDataOp, this operator can execute queries on SQL DB. The queries would be on data and not metadata.",
        "operator_name": "SQL Query Helper"
    },
    "UiTextOp": {
        "get_commands_help": ui_text_op.get_commands_help,
        "handle_command": lambda command: ui_text_op.handle_command(command),
        "file_name": "ui_text_op",
        "description": "This operator can send a reply to the user.",
        "operator_name": "UiText Operator"
    },
}

group_name = "postgres"
