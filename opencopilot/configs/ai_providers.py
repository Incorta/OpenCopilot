from enum import Enum


class SupportedAIProviders(Enum):
    openai = {
        "provider_name": "openai",
        "temperature": 0,
        "prompts_paths": {
            "planner": {
                "system": "resources/planner_level0_prompt_system.txt",
                "user": "resources/planner_level0_prompt_user.txt"
            },
            "executor": "resources/tasks_to_command_prompt.txt"
        }
    }
    azure_openai = {
        "provider_name": "azure_openai",
        "temperature": 0,
        "prompts_paths": {
            "planner": {
                "system": "resources/planner_level0_prompt_system.txt",
                "user": "resources/planner_level0_prompt_user.txt"
            },
            "executor": "resources/tasks_to_command_prompt.txt"
        }
    }
    google_gemini = {
        "provider_name": "google_gemini",
        "temperature": 0,
        "prompts_paths": {
            "planner": {
                "system": "resources/planner_level0_prompt_system.txt",
                "user": "resources/planner_level0_prompt_user.txt"
            },
            "executor": "resources/tasks_to_command_prompt.txt"
        }
    }
    mistral = {
        "provider_name": "mistral",
        "temperature": 0.1,
        "prompts_paths": {
            "planner": {
                "system": "resources/planner_level0_prompt_system.txt",
                "user": "resources/planner_level0_prompt_user.txt"
            },
            "executor": "resources/tasks_to_command_prompt.txt"
        }
    }


def get_model_by_name(provider_name):
    for model in SupportedAIProviders:
        if model.value['provider_name'] == provider_name:
            return model
    return None


def get_model_temperature(provider_name):
    model = get_model_by_name(provider_name)
    return model.value['temperature']


def get_planner_prompt_file_path(provider_name, prompt_type):
    model = get_model_by_name(provider_name)
    return model.value['prompts_paths']['planner'][prompt_type]


def get_executor_prompt_file_path(provider_name):
    model = get_model_by_name(provider_name)
    return model.value['prompts_paths']['executor']