import os
# OPERATORS CONFIGURATIONS
operators_path = os.getenv("OPERATORS_GROUPS", "YOUR.OPERATOR_GROUPS_PATH.OPERATOR1")

use_callback = True
test_env = os.getenv("TEST_ENVIRONMENT", "")
# EMBEDDING CREDENTIALS
embedding_api_key = os.getenv("OPENAI_AZURE_INCORTA_API_KEY", "")
embedding_api_type = os.getenv("OPENAI_GPT35_API_TYPE", "")
embedding_api_base = os.getenv("OPENAI_GPT35_API_BASE", "")
embedding_api_version = os.getenv("OPENAI_GPT35_API_VERSION", "")
embedding_api_engine = os.getenv("OPENAI_GPT35_API_ENGINE", "")

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

