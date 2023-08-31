import json
from opencopilot.configs.LLM_Configurations import LLMConfigurations
from opencopilot.utils.langchain import llm_GPT


class PostgresLLMConfigurations(LLMConfigurations):
    @classmethod
    def get_configurations(cls):
        return cls.retrieve_configs_from_file()

    @staticmethod
    def retrieve_configs_from_file():
        with open('service/configs/llm_copilot_configuration.json', 'r') as config_file:
            return json.load(config_file)


def register_postgres_gpt_configurations():
    LLMConfigurations.register(PostgresLLMConfigurations.get_configurations)
    llm_GPT.initialize_configurations()
