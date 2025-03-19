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

    @staticmethod
    def prepare_history_object(operator, tasks, context):
        for task in tasks:
            operator_name = task.get(constants.Operator, "")
            if operator_name == "":
                return {}
            operator = operators_handler_module.op_functions_resolver(context)[operator_name]
            operator_file = importlib.import_module(operator["file_name"])
            if hasattr(operator_file, "process_result_for_summary"):
                return operator_file.process_result_for_summary(tasks, operator_name)
