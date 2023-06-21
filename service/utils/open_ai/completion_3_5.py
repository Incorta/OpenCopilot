import json

import openai
from configs.env import openai_gpt35_api_key, openai_gpt35_api_base, openai_gpt35_api_type, openai_gpt35_api_version, \
    openai_gpt35_api_engine
import utils.logger as logger
from utils.exceptions import APIFailureException
import time


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
    if openai_gpt35_api_type == "azure":
        openai.api_type = "azure"
        openai.api_version = openai_gpt35_api_version
        openai.api_base = openai_gpt35_api_base
    else:
        openai.api_type = "open_ai"
        openai.api_version = ""
        openai.api_base = "https://api.openai.com/v1"
    openai.api_key = openai_gpt35_api_key

    logger.system_message("Calling GPT 3.5 with: \n")
    logger.operator_input(messages)
    # Send the prompt to the OpenAI API using gpt-3.5-turbo
    backoff_time = 2

    while True:
        try:
            if openai_gpt35_api_type == "azure":
                response = openai.ChatCompletion.create(
                    engine=openai_gpt35_api_engine,
                    temperature=0.2,
                    messages=messages
                )
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    temperature=0.2,
                    messages=messages,
                    request_timeout=1
                )

            # If the request is successful, exit the loop
            break

        except openai.error.RateLimitError:  # If a RateLimitError is thrown
            logger.error(f"ChatGPT Model is busy, retrying again in {backoff_time} seconds")
            time.sleep(backoff_time)  # Wait for 2 seconds

        except openai.error.Timeout:
            logger.error(f"Failed to get response from ChatGPT, retrying again in {backoff_time} seconds")
            time.sleep(backoff_time)  # Wait for 2 seconds

        except Exception as e:  # If any other exception is thrown
            print(f"Error class: {e.__class__.__name__}")
            raise APIFailureException(f"ChatGPT error occurred: {e}")

    if "choices" in response:
        # Extract the answer from the response
        answer = response.choices[0].message.content.strip()
        if parse_as_json:
            return extract_json_block(answer)
        else:
            return answer

    else:
        logger.error("chatGPT Failed to handle request")
        logger.error(response)
        raise APIFailureException("Failed while calling openAI API")
