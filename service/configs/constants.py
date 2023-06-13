# Session Query
session_query = "session_query"
session_query_list = "queries_list"
session_query_tasks = "tasks"
session_query_store = "store"
session_query_user_query_msg = "user_query_msg"
session_query_cached_agent_communications = "cached_agent_communications"
session_query_pending_agent_communications = "pending_agent_communications"
session_query_leve0_plan = "level0_plan"
session_query_operators = "operators"

# Operators
QueryOp = "QueryOp"
UiChartOp = "UiChartOp"
BusinessViewFinderOp = "BusinessViewFinderOp"
UiTextOp = "UiTextOp"

# Operator blocks
Command = "command"
Request = "request"
RequestText = "request_text"
Response = "response"
Status = "status"
Result = "result"
EnhancedResult = "enhanced_result"
RequireResultSummary = "require_result_summary"
Args = "args"
Operator = "operator"
Tasks = "tasks"
SubTasks = "sub-tasks"

DONE = "DONE"
TODO = "TODO"

OPERATORS_FILES = {
    QueryOp: "operators.incorta.query_op",
    UiChartOp: "operators.incorta.ui_chart_op",
    UiTextOp: "operators.incorta.ui_text_op",
    BusinessViewFinderOp: "operators.incorta.business_view_finder_op"
}
