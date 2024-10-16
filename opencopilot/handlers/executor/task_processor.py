import copy
import importlib
import json
from opencopilot.configs import constants
from opencopilot.configs.ai_providers import get_executor_prompt_file_path
from opencopilot.configs.env import operators_path
from opencopilot.utils import jinja_utils
from opencopilot.utils import logger, exceptions
from opencopilot.utils.langchain import llm_GPT
from opencopilot.utils.langchain.llm_GPT import resolve_llm_model
from opencopilot.utils.llm_evaluator import evaluate_llm_reply

operators_handler_module = importlib.import_module(operators_path + ".operators_handler")


def formulate_tasks(tasks, dependencies, task_index):
    for i, _ in enumerate(tasks):
        if tasks[i]["id"] not in dependencies and i != task_index:
            result = str(tasks[i]["result"])
            tasks[i]["result"] = "".join(result.split()[:5]) + "..."
    return tasks


def get_command_prompt_from_task(query_str, tasks, task_index, session, model, session_query=None, session_summary=None):
    task = tasks[task_index]

    # Check that the task's operator exists in the operators' group op_functions and get its command help
    if task[constants.Operator] in operators_handler_module.op_functions:
        commands_help = operators_handler_module.op_functions[task[constants.Operator]]["get_commands_help"](session_query, session)
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

    tasks_subset = copy.deepcopy(tasks[:tasks_count])
    if "depends_on_output_of" in tasks[task_index]:
        formulated_tasks = formulate_tasks(tasks_subset, task["depends_on_output_of"], task_index)
    else:
        formulated_tasks = tasks

    history = {}
    if "previous_interactions" in tasks[task_index]:
        history = {str(idx): session_summary[str(idx)] for idx in tasks[task_index]["previous_interactions"]}
    history_str = json.dumps(history, indent=2) if len(history) > 0 else ""

    prompt_text = jinja_utils.load_template(get_executor_prompt_file_path(model["ai_provider"]), {
        "query_str": query_str,
        "tasks": json.dumps(formulated_tasks),
        "curTaskId": task["id"],
        "commands_overview": commands_help["overview"],
        "commands": commands_help["commands"],
        "tasksLength": tasks_count,
        "sub_tasks_expectations": sub_tasks_expectations,
        "service_name": operators_handler_module.group_name,
        "history": history_str
    })
    messages = [{"role": "user", "content": prompt_text}]

    return messages


def get_command_from_task(query_str, tasks, task_index, session_entry, consumption_tracker, session_summary, evaluator, evaluate_response, session):
    model = resolve_llm_model(operators_handler_module.op_functions[tasks[task_index]["operator"]]["preferred_LLM"])

    # -- Build request
    messages = get_command_prompt_from_task(query_str=query_str,
                                            tasks=tasks,
                                            task_index=task_index,
                                            session=session,
                                            model=model,
                                            session_query=session_entry,
                                            session_summary=session_summary)
    logger.system_message("Creating command from task description")
    logger.print_gpt_messages(messages)
    session_entry.set_pending_agent_communications(component=task_index, sub_component="request", value=copy.deepcopy(messages))

    # -- Get command
    command = None
    cached_operator_command = session_entry.get_cached_agent_communications_operator_command(task_index, messages)

    if cached_operator_command is not None:
        command = cached_operator_command

    operator_name = operators_handler_module.op_functions[tasks[task_index]["operator"]]["operator_name"]
    if command is None:
        chat_gpt_response, consumption_tracking, _ = llm_GPT.run(messages, model)
        consumption_tracker.add_consumption(consumption_tracking, constants.executor, operator_name)
        if evaluate_response:
            evaluation, evaluation_consumption_tracking = evaluate_llm_reply(messages, chat_gpt_response)
            evaluator.add_llm_evaluation(evaluation, constants.executor, operator_name)
            consumption_tracker.add_consumption(evaluation_consumption_tracking, constants.executor, "* Evaluation - " + operator_name)

        command = json.loads(chat_gpt_response)

    logger.system_message("Got Command, will execute it:")
    logger.operator_response(json.dumps(command))

    if isinstance(command, list) and len(command) > 0:  # Sometimes it would come as an array
        command = command[0]

    return command
