import importlib
from abc import ABC, abstractmethod
from opencopilot.configs import constants
from opencopilot.configs.env import operators_path

operators_handler_module = importlib.import_module(operators_path + ".operators_handler")


class OperatorExecutor(ABC):
    @abstractmethod
    def execute(self, task_context, operator):
        pass

    @staticmethod
    def finalize(task_context, result):
        task_context.tasks[task_context.task_index][constants.Status] = constants.DONE
        task_context.tasks[task_context.task_index][constants.Result] = result
