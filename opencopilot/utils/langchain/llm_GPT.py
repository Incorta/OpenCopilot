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
from opencopilot.configs.ai_providers import SupportedAIProviders, get_model_temperature
from opencopilot.utils.consumption_tracker import ConsumptionTracker
from opencopilot.utils.exceptions import APIFailureException, UnsupportedAIProviderException, LLMException
from langchain_community.callbacks import get_openai_callback
from langchain_google_genai import ChatGoogleGenerativeAI

from opencopilot.utils.utilities import extract_json_block

LLM_RETRY_COUNT = 3


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
            try:
                response = extract_json_block(llm_reply_text)
            except Exception as e:
                raise APIFailureException(str(e))
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
    if model.ai_provider == SupportedAIProviders.openai.value["provider_name"]:
        return ChatOpenAI(
            api_key=model.api_key,
            base_url=model.api_base_url,
            model=model.model_name,
            temperature=get_model_temperature(model.ai_provider),
            max_tokens=4096,
        ), model.model_name
    elif model.ai_provider == SupportedAIProviders.azure_openai.value["provider_name"]:
        return AzureChatOpenAI(
            openai_api_key=model.api_key,
            openai_api_version="2023-05-15",
            azure_endpoint=model.api_base_url,
            deployment_name=model.model_name,
            temperature=get_model_temperature(model.ai_provider),
        ), model.model_name
    elif model.ai_provider == SupportedAIProviders.google_gemini.value["provider_name"]:
        return ChatGoogleGenerativeAI(
            model=model.model_name,
            google_api_key=model.api_key,
            temperature=get_model_temperature(model.ai_provider),
            convert_system_message_to_human=True
        ), model.model_name
    elif model.ai_provider == SupportedAIProviders.aixplain.value["provider_name"]:
        os.environ["TEAM_API_KEY"] = model.api_key
        from opencopilot.utils.langchain.aixplain import AixplainChatModel
        return AixplainChatModel(
            model_id=model.model_name,
            temperature=get_model_temperature(model.ai_provider),
            max_tokens=4096
        ), model.model_name
    else:
        raise UnsupportedAIProviderException("Unsupported AI Provider")
