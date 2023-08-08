import json
from opencopilot.configs.env import llm_api_engine, llm_api_type, llm_api_key, llm_api_base, llm_api_version
import opencopilot.utils.logger as logger
from opencopilot.utils.exceptions import APIFailureException
from langchain.llms import AzureOpenAI
from langchain import ConversationChain


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


def run(messages, parse_as_json=True):
    """ Assuming that we work with asure for now """

    logger.system_message("Calling LLM with: \n")
    logger.operator_input(messages)

    llm = None

    while True:
        try:
            if llm_api_type == "azure":
                llm = AzureOpenAI(
                    engine="gpt35-model",
                    model_name="gpt-3.5-turbo",
                    temperature=0
                )
            else:
                logger.system_message("OPENAI Unsupported in LLM yet!")

            break

        except Exception as e:  # If any other exception is thrown
            print(f"Error class: {e.__class__.__name__}")
            raise APIFailureException(f"ChatG PT error occurred: {e}")

    conversation = ConversationChain(llm=llm, verbose=True)
    response = conversation.predict(input=str(messages))

    return response
