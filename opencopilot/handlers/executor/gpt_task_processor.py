import importlib
import json
from opencopilot.configs import env, constants
from opencopilot.configs.env import operators_path
from opencopilot.utils import jinja_utils
from opencopilot.utils import logger, exceptions
from opencopilot.utils.exceptions import UnknownCommandError
from opencopilot.utils.open_ai import completion_3_5

operators_handler_module = importlib.import_module(operators_path + ".operators_handler")


def get_command_prompt_from_task(query_str, tasks, task_index, target="PLANNER"):
    task = tasks[task_index]

    # Check that the task's operator exists in the operators' group op_functions and get its command help
    if task[constants.Operator] in operators_handler_module.op_functions:
        commands_help = operators_handler_module.op_functions[task[constants.Operator]]["get_commands_help"]()
    else:
        raise exceptions.UnknownCommandError(f"Unknown command operator: {task[constants.Operator]}")

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
        "commands_command1_description": json.dumps([commands_help["commands"][0]["command_description"]], indent=2),
        "commands_command1": json.dumps([commands_help["commands"][0]["command"]], indent=2),
        "tasksLength": tasks_count,
        "sub_tasks_expectations": sub_tasks_expectations,
        "service_name": operators_handler_module.group_name
    })

    return prompt_text


def get_command_from_task(query_str, tasks, task_index, session_entry):
    prompt_text = get_command_prompt_from_task(query_str, tasks, task_index, "EXECUTOR")

    logger.system_message("Calling ChatGPT 3.5, to create command from task description")
    messages = [{"role": "system", "content": prompt_text}]
    logger.print_gpt_messages(messages)

    session_entry.set_pending_agent_communications(component=task_index, sub_component="request", value=messages)

    """ If get_op_command is enabled, retrieve operator's command from sessions_store instead of requesting it from GPT """
    command = None
    if env.sessions_getting_mode and (env.get_all or env.get_op_command):
        command = session_entry.get_cached_agent_communications(component=task_index, sub_component=constants.Command)

    if command is None:
        chat_gpt_response = completion_3_5.run(
            messages
        )
        command = json.loads(chat_gpt_response)

    logger.system_message("Got Command, will execute it:")
    logger.operator_response(json.dumps(command))

    if isinstance(command, list) and len(command) > 0:  # Sometimes it would come as an array
        command = command[0]

    return command


def enhance_and_finalize_task_result(command, task, task_index, session_entry):
    prompt_text = jinja_utils.load_template("resources/finalize_task_prompt.txt", {
        "taskJson": json.dumps(task),
        "initialCommand": json.dumps(command)
    })

    logger.system_message("Calling ChatGPT 3.5, to fine tune, and finalize task result")
    messages = [{"role": "system", "content": prompt_text}]
    logger.print_gpt_messages(messages)

    """ If get_op_enhanced_result is enabled, retrieve operator's enhanced_result from sessions_store instead of requesting it from GPT """
    chat_gpt_response = None
    if env.sessions_getting_mode and (env.get_all or env.get_op_enhanced_result):
        chat_gpt_response = session_entry.get_cached_agent_communications(component=task_index, sub_component=constants.EnhancedResult)

    if chat_gpt_response is None:
        chat_gpt_response = completion_3_5.run(
            messages
        )

    logger.system_message("Got final task result")
    logger.operator_response(chat_gpt_response)

    return json.loads(chat_gpt_response)
