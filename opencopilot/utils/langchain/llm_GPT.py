import json
import opencopilot.utils.logger as logger
from opencopilot.configs.env import llm_models_configurations, use_human_for_gpt_4
from opencopilot.utils.exceptions import APIFailureException
from langchain.llms import AzureOpenAI
from langchain import OpenAI
from opencopilot.utils.open_ai import common

llm_configs = json.loads(llm_models_configurations)


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
    model = None

    for llm_model in llm_names:
        if llm_model in llm_configs:
            model = llm_model
            break

    if model is None:
        print("Didn't find configurations of any of the desired models, Please set the configuration of the desired "
              "model in the env!")
        return None

    logger.system_message(str("Calling LLM-" + model + " with: \n"))
    logger.operator_input(messages)

    if use_human_for_gpt_4 and "GPT4" in model:
        return common.get_gpt_human_input(messages)

    engine = llm_configs[model]["engine"]
    model_name = llm_configs[model]["model_name"]
    key = llm_configs[model]["key"]
    version = llm_configs[model]["version"]
    base = llm_configs[model]["base"]

    if "Azure" in model:
        llm = AzureOpenAI(
            openai_api_key=key,
            api_version=version,
            api_type="azure",
            api_base=base,
            engine=engine,
            model_name=model_name,
            temperature=0
        )
    elif "OpenAI" in model:
        llm = OpenAI(
            openai_api_key=key,
            api_version="2023-05-15",
            api_type="azure",
            engine=engine,
            model_name=model_name,
            temperature=0
        )
    else:
        logger.system_message("Unknown AI Provider!")

    llm_reply = llm(str(messages))
    return extract_json_block(llm_reply)
