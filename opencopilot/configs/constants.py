from enum import Enum

# Session Query
session_query = "session_query"
session_query_tasks = "tasks"
session_query_store = "store"
session_query_user_query_msg = "user_query_msg"
session_query_level0_plan = "level0_plan"
session_query_operators = "operators"
session_timeout = 60 * 60
planner = "planner"
executor = "executor"

# Operator blocks
Command = "command"
Request = "request"
RequestText = "request_text"
Response = "response"
Status = "status"
Result = "result"
EnhancedResult = "enhanced_result"
Args = "args"
Operator = "operator"
Tasks = "tasks"
SubTasks = "sub-tasks"

DONE = "DONE"
TODO = "TODO"


class LLMModelPriority(Enum):
    primary_model = "primary_model"
    secondary_model = "secondary_model"
