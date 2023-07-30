import copy
import importlib
import json
from opencopilot.configs import env, constants
from opencopilot.configs.env import operators_path
from opencopilot.handlers.planner.gpt_planner import compare_requests
from opencopilot.utils import jinja_utils
from opencopilot.utils import logger, exceptions
from opencopilot.utils.exceptions import UnknownCommandError
from opencopilot.utils.open_ai import completion_3_5, completion_4

operators_handler_module = importlib.import_module(
    operators_path + ".operators_handler")


def get_command_prompt_from_task(query_str, tasks, task_index, target="PLANNER"):
    task = tasks[task_index]

    # Check that the task's operator exists in the operators' group op_functions and get its command help
    if task[constants.Operator] in operators_handler_module.op_functions:
        commands_help = operators_handler_module.op_functions[task[constants.Operator]]["get_commands_help"]()
        commands_help["overview"] = operators_handler_module.op_functions[task[constants.Operator]]["description"]
    else:
        raise exceptions.UnknownCommandError(
            f"Unknown command operator: {task[constants.Operator]}")

    sub_tasks_expectations = None
    if "expected_sub_tasks_count" in commands_help:
        sub_tasks_expectations = {
            "expected_count": commands_help["expected_sub_tasks_count"]
        }

    tasks_count = task_index + 1

    if target == "PLANNER":
        template_path = "resources/planner_level1_prompt.txt"
    elif target == "EXECUTOR":
        template_path = "resources/tasks_to_command_prompt.txt"

    else:
        raise UnknownCommandError(f"Unknown target: {target}")

    prompt_text = jinja_utils.load_template(template_path, {
        "query_str": query_str,
        "tasks": json.dumps(tasks[:tasks_count], indent=2),
        "curTaskId": task["id"],
        "commands_overview": commands_help["overview"],
        "commands": commands_help["commands"],
        "tasksLength": tasks_count,
        "sub_tasks_expectations": sub_tasks_expectations,
        "service_name": operators_handler_module.group_name
    })

    return prompt_text


def get_command_from_task(query_str, tasks, task_index, session_entry):
    prompt_text = get_command_prompt_from_task(
        query_str, tasks, task_index, "EXECUTOR")

    logger.system_message("Creating command from task description")
    messages = [{"role": "system", "content": prompt_text}]
    logger.print_gpt_messages(messages)

    session_entry.set_pending_agent_communications(
        component=task_index, sub_component="request", value=copy.deepcopy(messages))

    """ If get_op_command is enabled, retrieve operator's command from sessions_store instead of requesting it from GPT """
    command = None
    if env.sessions_getting_mode and (env.get_all or env.get_op_command):
        task_to_command_request = session_entry.get_cached_agent_communications(component=task_index, sub_component=constants.Request)
        if task_to_command_request and compare_requests(messages, task_to_command_request):
            command = session_entry.get_cached_agent_communications(component=task_index, sub_component=constants.Command)
        else:
            logger.system_message("Your request to the executor agent has changed, will regenerate the command!")

    preferred_LLM = operators_handler_module.op_functions[tasks[task_index]
                                                          ["operator"]]["preferred_LLM"]
    if command is None:
        logger.system_message(f"Calling ChatGPT {preferred_LLM}:")
        if preferred_LLM == "GPT-4":
            chat_gpt_response = completion_4.run(
                messages
            )
        else:
            chat_gpt_response = completion_3_5.run(
                messages
            )
        command = json.loads(chat_gpt_response)

    logger.system_message("Got Command, will execute it:")
    logger.operator_response(json.dumps(command))

    if isinstance(command, list) and len(command) > 0:  # Sometimes it would come as an array
        command = command[0]

    return command

