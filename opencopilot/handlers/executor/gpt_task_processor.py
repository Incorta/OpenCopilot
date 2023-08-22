import copy
import importlib
import json
from opencopilot.configs import env, constants
from opencopilot.configs.env import operators_path
from opencopilot.utils import jinja_utils
from opencopilot.utils import logger, exceptions
from opencopilot.utils.exceptions import UnknownCommandError
from opencopilot.utils.langchain import llm_GPT

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

    # -- Build request
    prompt_text = get_command_prompt_from_task(
        query_str, tasks, task_index, "EXECUTOR")
    logger.system_message("Creating command from task description")
    messages = [{"role": "system", "content": prompt_text}]
    logger.print_gpt_messages(messages)
    session_entry.set_pending_agent_communications(
        component=task_index, sub_component="request", value=copy.deepcopy(messages))

    # -- Get command
    command = None
    cached_operator_command = session_entry.get_cached_agent_communications_operator_command(task_index, messages)

    if cached_operator_command is not None:
        command = cached_operator_command

    if command is None:
        chat_gpt_response = llm_GPT.run(
            messages,
            [constants.GPTModel.AZURE_OPENAI_GPT3.value]
        )
        
        command = json.loads(chat_gpt_response)

    logger.system_message("Got Command, will execute it:")
    logger.operator_response(json.dumps(command))

    if isinstance(command, list) and len(command) > 0:  # Sometimes it would come as an array
        command = command[0]

    return command

