from abc import ABC
from opencopilot.utils.langchain import llm_GPT


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
