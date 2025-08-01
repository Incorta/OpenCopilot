import importlib
from abc import ABC, abstractmethod
from opencopilot.configs import constants


class OperatorExecutor(ABC):
    @abstractmethod
    def execute(self, task_context, operator):
        pass

    @staticmethod
    def finalize(task_context, result):
        task_context.tasks[task_context.task_index][constants.Result] = result

    @staticmethod
    def prepare_history_object(operator, tasks):
        operator_file = importlib.import_module(operator["file_name"])
        if hasattr(operator_file, "process_result_for_summary"):
            return operator_file.process_result_for_summary(tasks)
