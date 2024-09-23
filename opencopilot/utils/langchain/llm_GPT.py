import json
import os
from time import sleep

import langchain
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import opencopilot.utils.logger as logger
from opencopilot.configs.LLM_Configurations import LLMConfigurations
from opencopilot.configs.ai_providers import SupportedAIProviders, get_model_temperature
from opencopilot.utils.consumption_tracker import ConsumptionTracker
from opencopilot.utils.exceptions import APIFailureException, UnsupportedAIProviderException, LLMException
from opencopilot.configs.constants import LLMModelPriority
from langchain_community.callbacks import get_openai_callback
from langchain_google_genai import ChatGoogleGenerativeAI

llm_configs = None
LLM_RETRY_COUNT = 3


def initialize_configurations():
    global llm_configs
    llm_configs = LLMConfigurations.execute()


def update_configurations(key1, value1, key2=None, value2=None):
    llm_configs[LLMModelPriority.primary_model.value][key1] = value1
    if key2 is not None:
        llm_configs[LLMModelPriority.secondary_model.value][key2] = value2


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


def resolve_llm_model(llm_names, priority_list_mode=True):
    model = None
    if priority_list_mode:
        # Select the first found configured model
        for llm_model in llm_names:
            if llm_model in llm_configs and "ai_provider" in llm_configs[llm_model]:
                model = llm_configs[llm_model]
                break
    else:
        # Resolve extra predefined model
        model = llm_names

    if model is None:
        raise UnsupportedAIProviderException("Didn't find configurations of any of the desired models, "
                                             "Please set the configuration of the desired model in the env!")
    return model


def run(messages, model):
    llm, model_name = get_llm(model)

    logger.system_message(str("Calling LLM-" + model["ai_provider"] + " " + model_name + " with: \n"))
    logger.operator_input(messages)

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

    retry_count = 0
    while retry_count < LLM_RETRY_COUNT:
        try:
            with get_openai_callback() as cb:
                langchain.llm_cache = None
                llm_reply = llm.invoke(langchain_messages)
                consumption_tracking = ConsumptionTracker.create_consumption_unit(model_name, cb.total_tokens, cb.prompt_tokens, cb.completion_tokens, cb.successful_requests, cb.total_cost)

            llm_reply_text = llm_reply.content.replace("\\_", "_")  # to handle Mixtral tendency to escape underscores
            response = extract_json_block(llm_reply_text)
            return response, consumption_tracking, model_name
        except APIFailureException as e:
            retry_count += 1
            if retry_count < LLM_RETRY_COUNT:
                logger.system_message(f"[FAIL {retry_count}]: An APIFailureException occurred, retrying the call to {model['ai_provider'] + model_name}")
                llm.temperature += 0.1
                sleep(5)
                continue
            else:  # If it's the third failure, re-raise the exception
                raise LLMException(f"LLM encountered an error: {str(e)}") from e

        except Exception as e:
            raise LLMException(f"LLM encountered an error: {str(e)}") from e


def get_llm(model):
    logger.info(model)
    if model["ai_provider"] == SupportedAIProviders.openai.value["provider_name"]:
        return ChatOpenAI(
            api_key=model["openai_api_text_completion_key"],
            base_url=model.get("openai_api_text_completion_baseurl"),
            model=model["openai_api_text_completion_model_name"],
            temperature=get_model_temperature(model["ai_provider"]),
            max_tokens=4096,
        ), model["openai_api_text_completion_model_name"]
    elif model["ai_provider"] == SupportedAIProviders.azure_openai.value["provider_name"]:
        return AzureChatOpenAI(
            openai_api_key=model["azure_openai_text_completion_key"],
            openai_api_version="2023-05-15",
            azure_endpoint=model["azure_openai_text_completion_endpoint"],
            deployment_name=model["azure_openai_text_completion_deployment_name"],
            temperature=get_model_temperature(model["ai_provider"]),
        ), model["azure_openai_text_completion_deployment_name"]
    elif model["ai_provider"] == SupportedAIProviders.google_gemini.value["provider_name"]:
        return ChatGoogleGenerativeAI(
            model=model["google_gemini_text_completion_model_name"],
            google_api_key=model["google_gemini_text_completion_key"],
            temperature=get_model_temperature(model["ai_provider"]),
            convert_system_message_to_human=True
        ), model["google_gemini_text_completion_model_name"]
    elif model["ai_provider"] == SupportedAIProviders.aixplain.value["provider_name"]:
        os.environ["TEAM_API_KEY"] = model["aixplain_text_completion_key"]
        from opencopilot.utils.langchain.aixplain import AixplainChatModel
        return AixplainChatModel(
            model_id=model["aixplain_text_completion_model_id"],
            temperature=get_model_temperature(model["ai_provider"]),
            max_tokens=4096
        ), model["aixplain_text_completion_model_id"]
    else:
        raise UnsupportedAIProviderException("Unsupported AI Provider")
