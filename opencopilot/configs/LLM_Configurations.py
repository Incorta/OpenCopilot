from abc import ABC
from opencopilot.configs.env import use_callback
from opencopilot.utils.langchain import llm_GPT
import json

class LLMConfigurationsInterface(ABC):
    @classmethod
    def get_configurations(cls):
        pass


def register_callback(cb):
    global callback
    callback = cb
    llm_GPT.initialize_configurations()


def execute_callback():
    if callback is not None:
        return callback()
    else:
        raise NotImplementedError("Callback is not registered!")


def retrieve_configs_from_file():
    with open('service/configurations/llm_copilot_configuration.json', 'r') as config_file:
        config_data = json.loads(config_file)

    return config_data


def get_configs():
    if use_callback:
        return execute_callback()
    else:
        return retrieve_configs_from_file()
