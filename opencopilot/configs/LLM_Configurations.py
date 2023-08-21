from abc import ABC, abstractmethod

from opencopilot.utils.langchain import llm_GPT


class LLMConfigurationsInterface(ABC):
    @classmethod
    def get_configurations_from_cmc(cls):
        pass


def register_callback(cb):
    class IncortaLLMConfigurations(LLMConfigurationsInterface):

        global callback
    callback = cb
    llm_GPT.initialize_configurations()


def execute_callback_cmc():
    if callback is not None:
        return callback()
    else:
        print("No callback registered")
