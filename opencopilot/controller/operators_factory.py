import importlib
from opencopilot.configs.env import operators_path

operators_handler_module = importlib.import_module(operators_path + ".operators_handler")


class OperatorsFactory:
    @staticmethod
    def get_op_executor(operator):
        """
        Get the executor of an operator.

        Args:
            operator (dict): A dictionary containing operator details.

        Returns:
            An instance of the executor class.

        Raises:
            ValueError: If executor_class is not set or op_executor cannot be instantiated.
        """

        if "executor_class" in operator:
            executor_class = operator["executor_class"]

            # If executor_class is a string and 'executor_module_path' is in operator, import the module and get the class
            if isinstance(executor_class, str) and "executor_module_path" in operator:
                executor_module = importlib.import_module(operator["executor_module_path"])
                op_executor = getattr(executor_module, executor_class)
            # If executor_class is an instance of OperatorExecutor, assign it to op_executor directly
            else:
                op_executor = executor_class

            # If op_executor is still None, raise an error
            if op_executor is None:
                raise ValueError('Invalid op_executor name')

            # Return an instance of the executor class
            return op_executor()
        else:
            # Raise an error if 'executor_class' is not set in the operator dictionary
            raise ValueError("executor_class must be set")
