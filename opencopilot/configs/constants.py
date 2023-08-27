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
    OPENAI_GPT3 = "openai_gpt-3.5-turbo"
    OPENAI_GPT4 = "openai_gpt-4"
    AZURE_OPENAI_GPT3 = "azure-openai_gpt-3.5-turbo"
    AZURE_OPENAI_GPT4 = "azure-openai_gpt-4"
