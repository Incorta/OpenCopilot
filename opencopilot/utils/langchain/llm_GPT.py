import json
import os

from opencopilot.configs.env import llm_api_engine, llm_api_type, llm_api_key, llm_api_base, llm_api_version, \
    use_human_for_gpt_4
import opencopilot.utils.logger as logger
from opencopilot.utils.exceptions import APIFailureException
from langchain.llms import AzureOpenAI
from langchain import ConversationChain, OpenAI
from opencopilot.utils.open_ai import common


def run(messages, preferred_LLM="GPT-3.5", parse_as_json=True):

    logger.system_message(str("Calling LLM-" + preferred_LLM + " with: \n"))
    logger.operator_input(messages)

    if use_human_for_gpt_4 and preferred_LLM == "GPT-4":
        return common.get_gpt_human_input(messages)

    if preferred_LLM == "GPT-4":
        engine = "gpt4-model"
        model_name = "gpt-4"
    else:
        engine = "gpt35-model"
        model_name = "gpt-3.5-turbo"

    while True:
        try:
            if llm_api_type == "azure":
                llm = AzureOpenAI(
                    engine=engine,
                    model_name=model_name,
                    temperature=0
                )
            elif llm_api_type == "openai":
                llm = OpenAI(
                    engine=engine,
                    model_name=model_name,
                    temperature=0
                )
            else:
                logger.system_message("Unknown AI Provider!")

            break

        except Exception as e:  # If any other exception is thrown
            print(f"Error class: {e.__class__.__name__}")
            raise APIFailureException(f"ChatG PT error occurred: {e}")

    return llm(str(messages))
