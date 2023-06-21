from operators.postgres import query_op, table_finder_op, ui_text_op

op_functions = {
    "TableFinderOp": {
        "get_commands_help": table_finder_op.get_commands_help,
        "handle_command": lambda command: table_finder_op.handle_command(command),
        "file_name": "table_finder_op",
        "description": "All queries must be against a single table, this operator can help you find the most relevant table.",
        "operator_name": "SQL Metadata Helper"
    },
    "QueryOp": {
        "get_commands_help": query_op.get_commands_help,
        "handle_command": lambda command: query_op.handle_command(command),
        "file_name": "query_op",
        "description": "This operator requires input from the TableFinderOp, this operator can execute queries on SQL DB. The queries would be on data and not metadata.",
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
