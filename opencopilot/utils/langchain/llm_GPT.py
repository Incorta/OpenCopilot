import json
import langchain.llms as llms
import opencopilot.utils.logger as logger
from opencopilot.configs.LLM_Configurations import LLMConfigurations
from opencopilot.configs.env import use_human_for_gpt_4
from opencopilot.utils import network
from opencopilot.utils.exceptions import APIFailureException, UnsupportedAIProviderException
from opencopilot.utils.open_ai import common
from opencopilot.configs.constants import LLMModelName
llm_configs = None


def initialize_configurations():
    global llm_configs
    llm_configs = LLMConfigurations.execute()


def extract_json_block(text):
    # Find the first and last curly brace
    start_index = text.find("{")
    end_index = text.rfind("}")

    if start_index != -1 and end_index != -1:
        # Extract the JSON block from the text
        json_block_text = text[start_index:end_index + 1]

        # Parse the JSON block into a Python dictionary
        json_block_dict = json.loads(json_block_text)

        # Print the extracted JSON block
        return json.dumps(json_block_dict, indent=4)
    else:
        raise APIFailureException("No JSON block found in the text.")


def run(messages, llm_names):
    llm = None
    model = None
    # Select the first found configured model
    for llm_model in llm_names:
        if llm_model in llm_configs:
            model = llm_model
            break

    if model is None:
        raise UnsupportedAIProviderException("Didn't find configurations of any of the desired models, "
                                             "Please set the configuration of the desired model in the env!")

    logger.system_message(str("Calling LLM-" + model + " with: \n"))
    logger.operator_input(messages)

    if use_human_for_gpt_4 and "gpt-4" in model:
        return common.get_gpt_human_input(messages)

    llm = get_llm(model)
    llm_reply = network.retry(
        lambda: llm(str(messages))
    )
    return extract_json_block(llm_reply)


def get_llm(model):
    if model == LLMModelName.azure_openai_gpt_4.value or model == LLMModelName.azure_openai_gpt_35_turbo.value:
        return llms.AzureOpenAI(
            model_name=llm_configs[model]["API Deployment Name"],
            openai_api_key=llm_configs[model]["API Key"],
            api_version=llm_configs[model]["API Deployment Version"],
            api_base=llm_configs[model]["API Endpoint"],
            api_type="azure",
            engine="gpt4-model" if model == LLMModelName.azure_openai_gpt_4.value else "gpt35-model",
            temperature=0
        )
    elif model == LLMModelName.openai_gpt_4.value or model == LLMModelName.openai_gpt_35_turbo.value:
        return llms.OpenAI(
            openai_api_key=llm_configs[model]["API Key"],
            engine="gpt4-model" if model == LLMModelName.azure_openai_gpt_4.value else "gpt35-model",
            temperature=0
        )
    else:
        raise UnsupportedAIProviderException("Unsupported AI Provider")
