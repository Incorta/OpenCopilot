import json
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import opencopilot.utils.logger as logger
from opencopilot.configs.LLM_Configurations import LLMConfigurations
from opencopilot.configs.env import use_human_for_gpt_4
from opencopilot.utils import network
from opencopilot.utils.consumption_tracker import ConsumptionTracker
from opencopilot.utils.exceptions import APIFailureException, UnsupportedAIProviderException
from opencopilot.utils.open_ai import common
from opencopilot.configs.constants import LLMModelName
from langchain.callbacks import get_openai_callback

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
        try:
            json_block_dict = json.loads(json_block_text)
        except json.JSONDecodeError as e:
            print("Error parsing JSON:")
            print(json_block_text)
            print("Exception:", str(e))
            raise APIFailureException("Error parsing JSON.")

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

    # Convert messages object to langchain messages model - TODO: it is better to use those objects from the beginning
    langchain_messages = []
    for message in messages:
        content = message["content"]
        if message["role"] == "system":
            langchain_messages.append(SystemMessage(content=content))
        elif message["role"] == "user":
            langchain_messages.append(HumanMessage(content=content))
        elif message["role"] == "assistant":
            langchain_messages.append(AIMessage(content=content))

    with get_openai_callback() as cb:
        llm_reply = network.retry(lambda: llm(langchain_messages))
        print(cb)
        consumption_tracking = ConsumptionTracker.create_consumption_unit(llm.model_name, cb.total_tokens, cb.prompt_tokens, cb.completion_tokens, cb.successful_requests, cb.total_cost)

    llm_reply_text = llm_reply.content
    return extract_json_block(llm_reply_text), consumption_tracking


def get_llm(model):
    if model == LLMModelName.azure_openai_gpt_4.value or model == LLMModelName.azure_openai_gpt_35_turbo.value:
        return AzureChatOpenAI(
            openai_api_key=llm_configs[model]["api_key"],
            openai_api_version=llm_configs[model]["api_deployment_version"],
            openai_api_base=llm_configs[model]["api_endpoint"],
            deployment_name=llm_configs[model]["api_deployment_name"], # Engine maps to the deployment name in Azure.
            model_name="gpt-4" if model == LLMModelName.azure_openai_gpt_4.value else "gpt-3.5-turbo", # Model name maps to the model to be used in this specific Azure deployment
            temperature=0
        )
    elif model == LLMModelName.openai_gpt_4.value or model == LLMModelName.openai_gpt_35_turbo.value:
        return ChatOpenAI(
            openai_api_key=llm_configs[model]["api_key"],
            model_name="gpt-4" if model == LLMModelName.openai_gpt_4.value else "gpt-3.5-turbo", # Engine in OPENAI maps to a specific model to be used.
            temperature=0
        )
    else:
        raise UnsupportedAIProviderException("Unsupported AI Provider")
