from time import sleep
from enum import StrEnum

import langchain
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain.callbacks.base import Callbacks
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from pydantic import BaseModel, Field, HttpUrl

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


# --- Pydantic Validation for Runtime Arguments ---
class ReasoningEffort(StrEnum):
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Verbosity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ConstructorArgs(BaseModel):
    """A strict schema for runtime constructor arguments."""
    temperature: float | None = Field(None, ge=0.0, le=2.0, description="The model's temperature.")
    max_tokens: int | None = Field(default=4096, gt=0, description="The maximum number of tokens to generate.")
    base_url: HttpUrl | None = None
    api_key: str | None = None
    model: str | None = None
    max_retries: int | None = Field(default=2, ge=0, description="Maximum number of retries.") # <-- Added here
    reasoning_effort: ReasoningEffort | None = None
    verbosity: Verbosity | None = None

    class Config:
        extra = 'forbid'


# -------------------------------------------------

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


def get_llm(model, runtime_kwargs: ConstructorArgs | None = None):
    """
    Instantiates an LLM client by merging provider, saved, and runtime configurations.

    Args:
        model: The LLMConfig object from the configuration files.
        runtime_kwargs (Optional[ConstructorArgs]): Validated runtime arguments that
                                                    override any other settings.
    """
    # 1. Prepare configuration layers

    # Layer 1: Provider-specific defaults (lowest precedence)
    provider_defaults = {
        "api_key": model.provider_args.get("api_key"),
        "base_url": model.provider_args.get("api_base_url"),
        "model": model.provider_args.get("model_name"),
        "temperature": get_model_temperature(model.provider),
    }

    # Layer 2: Arguments saved in the model's configuration file
    saved_config_kwargs = model.settings.get("constructor_args", {})

    # Layer 3: Runtime arguments from the Pydantic model (highest precedence)
    # Pydantic defaults (max_tokens=4096, max_retries=2) will be included here.
    runtime_args_dict = runtime_kwargs.model_dump() if runtime_kwargs else {}

    clean_provider_defaults = {k: (v.value if isinstance(v, StrEnum) else v) for k, v in provider_defaults.items() if v is not None}
    clean_saved_config = {k: (v.value if isinstance(v, StrEnum) else v) for k, v in saved_config_kwargs.items() if v is not None}
    clean_runtime_args = {k: (v.value if isinstance(v, StrEnum) else v) for k, v in runtime_args_dict.items() if v is not None}

    # 2. Merge all arguments with a clear precedence
    final_args = {
        **clean_provider_defaults, # lowest precedence
        **clean_saved_config,
        **clean_runtime_args, # highest precedence
        "callbacks": get_callback_handlers()
    }

    # 3. Instantiate the correct provider client

    # --- OpenAI Provider ---
    if model.provider == SupportedAIProviders.openai.value["provider_name"]:
        constructor_kwargs = {
            "api_key": final_args.get("api_key"),
            "base_url": str(final_args.get("base_url")) if final_args.get("base_url") else None,
            "model": final_args.get("model"),
            "temperature": final_args.get("temperature"),
            "max_tokens": final_args.get("max_tokens"),
            "max_retries": final_args.get("max_retries"),
            "callbacks": final_args.get("callbacks"),
        }
        # Filter out None values to avoid passing them to the constructor
        final_constructor_kwargs = {k: v for k, v in constructor_kwargs.items() if v is not None}
        return ChatOpenAI(**final_constructor_kwargs), final_args.get("model")

    # --- Azure OpenAI Provider ---
    elif model.provider == SupportedAIProviders.azure_openai.value["provider_name"]:
        constructor_kwargs = {
            "openai_api_key": final_args.get("api_key"),
            "openai_api_version": "2023-05-15",
            "azure_endpoint": str(final_args.get("base_url")) if final_args.get("base_url") else None,
            "deployment_name": final_args.get("model"),
            "temperature": final_args.get("temperature"),
            "max_tokens": final_args.get("max_tokens"),
            "max_retries": final_args.get("max_retries"),
            "callbacks": final_args.get("callbacks"),
        }
        final_constructor_kwargs = {k: v for k, v in constructor_kwargs.items() if v is not None}
        return AzureChatOpenAI(**final_constructor_kwargs), final_args.get("model")

    # --- Google Gemini Provider ---
    elif model.provider == SupportedAIProviders.google_gemini.value["provider_name"]:
        constructor_kwargs = {
            "google_api_key": final_args.get("api_key"),
            "model": final_args.get("model"),
            "temperature": final_args.get("temperature"),
            "max_tokens": final_args.get("max_tokens"),
            "callbacks": final_args.get("callbacks"),
            "convert_system_message_to_human": True,
        }
        final_constructor_kwargs = {k: v for k, v in constructor_kwargs.items() if v is not None}
        return ChatGoogleGenerativeAI(**final_constructor_kwargs), final_args.get("model")

    # --- Fallback for unsupported providers ---
    else:
        raise UnsupportedAIProviderException(
            f"Unsupported AI Provider: '{model.provider}'"
        )
    