from operators.postgres import query_op, metadata_op, ui_text_op


op_functions = {
    "MetaDataOp": {
        "get_commands_help": metadata_op.get_commands_help,
        "handle_command": lambda command: metadata_op.handle_command(command),
        "file_name": "metadata_op",
        "description": "This operator can help you find the most relevant table relevant to some query. It retrieves table names and its corresponding column names from the DB metadata.",
        "operator_name": "Metadata Operator",
        "preferred_LLM": "GPT-3.5"
    },
    "QueryOp": {
        "get_commands_help": query_op.get_commands_help,
        "handle_command": lambda command: query_op.handle_command(command),
        "file_name": "query_op",
        "description": "This operator can execute queries on SQL DB. The queries would be on data and not metadata. Before using this task, you must have the exact table name and columns names. You can do so from another task or if it is given by the user.",
        "operator_name": "Query Operator",
        "preferred_LLM": "GPT-4"
    },
    "UiTextOp": {
        "get_commands_help": ui_text_op.get_commands_help,
        "handle_command": lambda command: ui_text_op.handle_command(command),
        "file_name": "ui_text_op",
        "description": "This operator can sends text reply to the user.",
        "operator_name": "UiText Operator",
        "preferred_LLM": "GPT-3.5"
    },
}

group_name = "postgres"
