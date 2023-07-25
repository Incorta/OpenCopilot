import json
import openai
from opencopilot.configs.env import openai_gpt4_api_key, openai_gpt4_api_base, openai_gpt4_api_type, openai_gpt4_api_version, openai_gpt4_api_engine
import time
from opencopilot.configs.env import use_human_for_gpt_4
from opencopilot.utils.open_ai import common, completion_3_5
import opencopilot.utils.logger as logger
from opencopilot.utils.exceptions import APIFailureException


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
    # Send the prompt to the OpenAI API using gpt-4
    response = None
    
    if openai_gpt4_api_type == "azure":
        openai.api_type = "azure"
        openai.api_version = openai_gpt4_api_version
        openai.api_base = openai_gpt4_api_base
    else:
        openai.api_type = "open_ai"
        openai.api_version = ""
        openai.api_base = "https://api.openai.com/v1"
    openai.api_key = openai_gpt4_api_key

    if use_human_for_gpt_4:
        return common.get_gpt_human_input(messages)

    else:
        logger.system_message("Calling GPT 4 with: \n")
        logger.print_gpt_messages(messages)
        backoff_time = 2

        while True:
            try:
                if openai_gpt4_api_type == "azure":
                    response = openai.ChatCompletion.create(
                        engine=openai_gpt4_api_engine,
                        temperature=0,
                        messages=messages
                    )
                else:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        temperature=0,
                        messages=messages
                    )
                # If the request is successful, exit the loop
                break

            except openai.error.RateLimitError:  # If a RateLimitError is thrown
                logger.error(f"ChatGPT Model is busy, retrying again in {backoff_time} seconds")
                time.sleep(backoff_time)  # Wait for 2 seconds

            except Exception as e:  # If any other exception is thrown
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
