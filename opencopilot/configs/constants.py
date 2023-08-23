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

GPT3_ENGINE = "gpt35-model"
GPT4_ENGINE = "gpt4-model"


class LLMModelName(Enum):
    # Maps variables to model names
    OPENAI_GPT3 = "OPEN_AI_GPT3"
    OPENAI_GPT4 = "OPEN_AI_GPT4"
    AZURE_OPENAI_GPT3 = "AZURE_OPEN_AI_GPT3"
    AZURE_OPENAI_GPT4 = "AZURE_OPEN_AI_GPT4"
    EMBEDDING_Model = "EMBEDDING"


class ModelConfigurations(Enum):
    # Maps configurations of each model to its corresponding configuration
    API_DEPLOYMENT_NAME = "api_deployment_name"
    API_KEY = "api_key"
    API_DEPLOYMENT_VERSION = "api_deployment_version"
    API_ENDPOINT = "api_endpoint"
    ORGANIZATION = "organization"
    API_MODEL_NAME = "api_model_name"
    API_TYPE = "api_type"
