from enum import Enum

# Session Query
session_query = "session_query"
session_query_tasks = "tasks"
session_query_store = "store"
session_query_user_query_msg = "user_query_msg"
session_query_leve0_plan = "level0_plan"
session_query_operators = "operators"

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


class LLMModelName(Enum):
    # Maps variables to model names
    openai_gpt_35_turbo = "openai_gpt-35-turbo"
    openai_gpt_4 = "openai_gpt-4"
    azure_openai_gpt_35_turbo = "azure-openai_gpt-35-turbo"
    azure_openai_gpt_4 = "azure-openai_gpt-4"
    google_palm = "google_palm"
