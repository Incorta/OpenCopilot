from configs.env import operators_path
from operators.incorta import business_view_finder_op, ui_chart_op, ui_text_op, query_op

op_functions = {
    "BusinessViewFinderOp": {
        "get_commands_help": business_view_finder_op.get_commands_help,
        "handle_command": lambda command: business_view_finder_op.handle_command(command),
        "file_name": operators_path + ".business_view_finder_op",
        "description": "planner_level0_prompt.txt View, this operator can help you find the most relevant Business View",
        "operator_name": "Incorta Business Operator"
    },
    "UiChartOp": {
        "get_commands_help": ui_chart_op.get_commands_help,
        "handle_command": lambda command: ui_chart_op.handle_command(command),
        "file_name": operators_path + ".ui_chart_op",
        "description": "This operator can draw charts using data from the QueryOp operator",
        "operator_name": "Incorta UiChart Operator"
    },
    "UiTextOp": {
        "get_commands_help": ui_text_op.get_commands_help,
        "handle_command": lambda command: ui_text_op.handle_command(command),
        "file_name": operators_path + ".ui_text_op",
        "description": "This operator can send a reply to the user",
        "operator_name": "Incorta UiText Operator"
    },
    "QueryOp": {
        "get_commands_help": query_op.get_commands_help,
        "handle_command": lambda command: query_op.handle_command(command),
        "file_name": operators_path + ".query_op",
        "description": "This operator requires input from the BusinessViewFinderOp, this operator can execute queries on Incorta SQL. The queries would be on data and not metadata. This Operator can be used only once, with a coarse-grain request, with detailed schema.view.column info. And the query must contain one view only. There should be ONLY one task for this operator at most.",
        "operator_name": "Incorta Query Operator"
    }
}
