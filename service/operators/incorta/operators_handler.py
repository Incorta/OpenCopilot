from operators.incorta import business_view_finder_op, ui_chart_op, ui_text_op, query_op

op_functions = {
    "BusinessViewFinderOp": {
        "get_commands_help": business_view_finder_op.get_commands_help,
        "handle_command": lambda command: business_view_finder_op.handle_command(command),
        "file_name": "business_view_finder_op"
    },
    "UiChartOp": {
        "get_commands_help": ui_chart_op.get_commands_help,
        "handle_command": lambda command: ui_chart_op.handle_command(command),
        "file_name": "ui_chart_op"
    },
    "UiTextOp": {
        "get_commands_help": ui_text_op.get_commands_help,
        "handle_command": lambda command: ui_text_op.handle_command(command),
        "file_name": "ui_text_op"
    },
    "QueryOp": {
        "get_commands_help": query_op.get_commands_help,
        "handle_command": lambda command: query_op.handle_command(command),
        "file_name": "query_op"
    }
}
