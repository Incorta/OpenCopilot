import importlib
from opencopilot.configs.env import service_utils_path

service_utils_exceptions_module = importlib.import_module(service_utils_path + ".exceptions")


class UnknownCommandError(Exception):
    pass


class APIFailureException(Exception):
    pass


class IllegalArgumentException(Exception):
    pass


class UnauthorizedUserException(Exception):
    pass


class UnsupportedAIProviderException(Exception):
    pass


class ProviderNotFoundException(Exception):
    pass


class LLMException(service_utils_exceptions_module.CopilotException):
    """Base class for exceptions related to LLM operations."""

    def __init__(self, message):
        super().__init__(message, error_title="LLM service Error")
