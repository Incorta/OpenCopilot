import importlib
from collections import namedtuple
from opencopilot.configs import constants
from opencopilot.utils import logger
from opencopilot.configs.env import operators_path

operators_handler_module = importlib.import_module(operators_path + ".operators_handler")
UserQuery = namedtuple("UserQuery", ["user_query_str", "predefined_agent_communication"])


def create_user_query_tuple(query_str, predefined_obj):
    return UserQuery(query_str, predefined_obj)


def validate_predefined_query(query_object):
    predefined_object = query_object.predefined_agent_communication
    # Check object is not empty
    if not predefined_object:
        return False

    # Check that level 0 plan exists
    if not (constants.session_query_level0_plan in predefined_object
            and constants.Response in predefined_object[constants.session_query_level0_plan]
            and constants.Tasks in predefined_object[constants.session_query_level0_plan][constants.Response]):
        return False

    tasks = predefined_object[constants.session_query_level0_plan][constants.Response][constants.Tasks]
    tasks_count = len(tasks)

    operators = None
    # If one or more operator exists
    if constants.session_query_operators in predefined_object:
        operators = predefined_object[constants.session_query_operators]
        # Verify that operators are equal to tasks count
        if len(operators) != tasks_count:
            return False

    # Verify that existing operators are in the same order of the tasks
    for task_idx in range(len(operators)):
        operator = operators[task_idx]

        # Skip the operator validation if it contains an empty command
        if len(operator[constants.Command]) == 0:
            continue

        task = tasks[task_idx]
        task_operator = task[constants.Operator]
        operator_module = importlib.import_module(operators_handler_module.op_functions[task_operator]["file_name"])
        # Validate that command_name in operator's command is one of the Operators defined commands
        # A naive assertion for tasks equivalence with the plan's tasks
        #  (2 or more sequential tasks of the same operators that aren't in order will pass this even if they shouldn't)
        if task_idx <= len(operators) and operator[constants.Command]["command_name"] not in dir(operator_module.Commands):
            return False

    logger.predefined_message(f"Using Predefined agent communication object for query: '{query_object.user_query_str}'")
    return True
