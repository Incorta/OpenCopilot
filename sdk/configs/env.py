# Copy and remove the .example at the end

# OPERATORS CONFIGURATIONS
operators_group = "postgres"
operators_path = "operators." + operators_group

# DATABASE CONFIGURATIONS
db_host = "database"
db_name = "ecommerce"
db_user = "root"
db_password = "root"
db_port = "5432"

# CHAT_GPT3.5 CREDENTIALS
openai_gpt35_api_key = "e2f75a125cba4b3195861244e3df12f2"
openai_gpt35_api_type = "azure"
openai_gpt35_api_base = "https://test-gpt35.openai.azure.com"
openai_gpt35_api_version = "2023-05-15"
openai_gpt35_api_engine = "gpt35-model"

# CHAT_GPT4 CONFIGURATIONS
use_gpt_4 = False
openai_gpt4_api_key = ""
openai_gpt4_api_type = ""
openai_gpt4_api_base = ""
openai_gpt4_api_version = ""
openai_gpt4_api_engine = ""
use_human_for_gpt_4 = False

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
