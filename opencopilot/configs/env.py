import os
# OPERATORS CONFIGURATIONS
operators_path = os.getenv("OPERATORS_GROUPS", "YOUR.OPERATOR_GROUPS_PATH.OPERATOR1")

# CHAT_GPT3.5 CREDENTIALS
openai_gpt35_api_key = os.getenv("OPENAI_GPT35_API_KEY", "")
openai_gpt35_api_type = os.getenv("OPENAI_GPT35_API_TYPE", "")
openai_gpt35_api_base = os.getenv("OPENAI_GPT35_API_BASE", "")
openai_gpt35_api_version = os.getenv("OPENAI_GPT35_API_VERSION", "")
openai_gpt35_api_engine = os.getenv("OPENAI_GPT35_API_ENGINE", "")

# CHAT_GPT4 CONFIGURATIONS
use_gpt_4 = bool(os.getenv("USE_GPT_4", False))
openai_gpt4_api_key = os.getenv("OPENAI_GPT4_API_KEY", "")
openai_gpt4_api_type = os.getenv("OPENAI_GPT4_API_TYPE", "")
openai_gpt4_api_base = os.getenv("OPENAI_GPT4_API_BASE", "")
openai_gpt4_api_version = os.getenv("OPENAI_GPT4_API_VERSION", "")
openai_gpt4_api_engine = os.getenv("OPENAI_GPT4_API_ENGINE", "")
use_human_for_gpt_4 = bool(os.getenv("USE_HUMAN_FOR_GPT_4", False))

# CHROMA_DB INDEXING ENABLING
enable_ad_hoc_views_indexing = True
openai_text_ada_api_key = ""

## QUERIES CACHING ##
# SETTING MODE
sessions_setting_mode = True
overwrite_if_exists = True
# GETTING MODE
sessions_getting_mode = True  # Must be enabled to enable any of the following get_ flags
get_all = True
get_plan_response = True
get_op_command = True
get_op_result = True
get_op_enhanced_result = True

