import importlib
import json
import os
import sys

from opencopilot.configs.env import user_operators_path


class ExecutorsFactory:
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
            FileNotFoundError: If the manifest.json file is not found.
            ImportError: If the executor module or class cannot be imported.
        """
        op_executor = None

        # Case 1: Direct executor_class
        if "executor_class" in operator:
            executor_class = operator["executor_class"]
            if isinstance(executor_class, str) and "executor_module_path" in operator:
                try:
                    executor_module = importlib.import_module(operator["executor_module_path"])
                    op_executor = getattr(executor_module, executor_class, None)
                except ImportError as e:
                    raise ImportError(f"Failed to import executor class '{executor_class}': {e}")
            else:
                op_executor = executor_class

        # Case 2: Plugin-based executor
        elif "plugin_name" in operator:
            plugin_name = operator["plugin_name"]
            manifest_path = os.path.join(user_operators_path, plugin_name, "manifest.json")
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as manifest_file:
                    manifest_data = json.load(manifest_file)
                    executor_path = manifest_data.get("executorPath", "")
                    executor_class = manifest_data.get("executorClass", "")

                    if not executor_path or not executor_class:
                        raise ValueError(f"Invalid manifest.json: Missing executorPath or executorClass in {manifest_path}")

                    # Ensure the executor_path is a fully-qualified module path
                    if not executor_path.startswith("service_data.user_operators"):
                        # Prepend the base namespace to make it fully qualified
                        executor_path = f"service_data.user_operators.{executor_path}"
                    # Temporarily add user_operators_path to sys.path
                    sys.path.insert(0, user_operators_path)
                    try:
                        executor_module = importlib.import_module(executor_path)
                        op_executor = getattr(executor_module, executor_class, None)
                        if op_executor is None:
                            raise ImportError(f"Executor class '{executor_class}' not found in module '{executor_path}'")
                    except ImportError as e:
                        raise ImportError(f"Failed to import executor from manifest: {e}")
                    finally:
                        # Remove the custom path from sys.path to avoid side effects
                        sys.path.pop(0)
            else:
                raise FileNotFoundError(f"Manifest file not found at: {manifest_path}")

        else:
            raise ValueError("The operator must define either 'executor_class' or 'plugin_name'")

        # Ensure the executor is callable
        if not callable(op_executor):
            raise TypeError(f"The executor '{op_executor}' is not callable")

        # Return an instance of the executor class
        return op_executor()
