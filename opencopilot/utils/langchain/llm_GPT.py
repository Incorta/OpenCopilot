from time import sleep

import langchain
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain.callbacks.base import Callbacks
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import opencopilot.utils.logger as logger
from opencopilot.utils.utilities import extract_json_block
from opencopilot.configs.ai_providers import SupportedAIProviders, get_model_temperature
from opencopilot.configs.env import langfuse_public_key, langfuse_secret_key, langfuse_host
from opencopilot.utils.consumption_tracker import ConsumptionTracker
from opencopilot.utils.exceptions import APIFailureException, UnsupportedAIProviderException, LLMException
from langchain_community.callbacks import get_openai_callback
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse.callback import CallbackHandler


LLM_RETRY_COUNT = 3
callback_handlers: Callbacks | None = None

def get_callback_handlers() -> Callbacks:
    global callback_handlers
    if callback_handlers is None:
        callback_handlers = []
        if langfuse_public_key and langfuse_secret_key and langfuse_host:
            langfuse_handler = CallbackHandler(
                public_key=langfuse_public_key,
                secret_key=langfuse_secret_key,
                host=langfuse_host
            )
            callback_handlers.append(langfuse_handler)
    return callback_handlers


def run(messages, model):
    llm, model_name = get_llm(model)

    logger.system_message(str("Calling LLM-" + model.provider + " " + model_name + " with: \n"))
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
                logger.system_message(f"[FAIL {retry_count}]: An APIFailureException occurred, retrying the call to {model['provider'] + model_name}")
                llm.temperature += 0.1
                sleep(5)
                continue
            else:  # If it's the third failure, re-raise the exception
                raise LLMException(f"LLM encountered an error: {str(e)}") from e

        except Exception as e:
            raise LLMException(f"LLM encountered an error: {str(e)}") from e


def get_llm(model):

    # Get any extra constructor arguments from settings, defaulting to an empty dict
    # Safely get any extra constructor arguments from settings
    extra_kwargs = model.settings.get("constructor_args", {})
    # --- OpenAI Provider ---
    if model.provider == SupportedAIProviders.openai.value["provider_name"]:
        base_kwargs = {
            "api_key": model.provider_args.get("api_key"),
            "base_url": model.provider_args.get("api_base_url"),
            "model": model.provider_args["model_name"],
            "temperature": get_model_temperature(model.provider),
            "max_tokens": 4096,
            "callbacks": get_callback_handlers(),
        }
        final_kwargs = {**base_kwargs, **extra_kwargs}
        return ChatOpenAI(**final_kwargs), model.provider_args["model_name"]

    # --- Azure OpenAI Provider ---
    elif model.provider == SupportedAIProviders.azure_openai.value["provider_name"]:
        base_kwargs = {
            "openai_api_key": model.provider_args.get("api_key"),
            "openai_api_version": "2023-05-15",
            "azure_endpoint": model.provider_args.get("api_base_url"),
            "deployment_name": model.provider_args["model_name"],
            "temperature": get_model_temperature(model.provider),
            "callbacks": get_callback_handlers(),
        }
        final_kwargs = {**base_kwargs, **extra_kwargs}
        return AzureChatOpenAI(**final_kwargs), model.provider_args["model_name"]

    # --- Google Gemini Provider ---
    elif model.provider == SupportedAIProviders.google_gemini.value["provider_name"]:
        base_kwargs = {
            "model": model.provider_args["model_name"],
            "google_api_key": model.provider_args.get("api_key"),
            "temperature": get_model_temperature(model.provider),
            "convert_system_message_to_human": True,
            "callbacks": get_callback_handlers(),
        }
        final_kwargs = {**base_kwargs, **extra_kwargs}
        return ChatGoogleGenerativeAI(**final_kwargs), model.provider_args["model_name"]

    # --- Fallback for unsupported providers ---
    else:
        raise UnsupportedAIProviderException(
            f"Unsupported AI Provider: '{model.provider}'"
        )