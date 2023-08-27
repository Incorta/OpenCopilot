import copy
import json
import importlib
import opencopilot.utils.logger as logger
from opencopilot.configs import env, constants
from opencopilot.handlers.executor import gpt_task_processor
from opencopilot.configs.env import operators_path
from opencopilot.utils import jinja_utils
from opencopilot.utils.exceptions import UnknownCommandError
from opencopilot.utils.langchain import llm_GPT

operators_handler_module = importlib.import_module(operators_path + ".operators_handler")
planner_llm_models_list = [constants.LLMModelName.AZURE_OPENAI_GPT4.value, constants.LLMModelName.AZURE_OPENAI_GPT3.value]


def get_next_todo_task_index(tasks_list):
    i = 0
    for task in tasks_list:
        if task[constants.Status] == constants.TODO:
            return i
        i += 1

    return -1


def summarize_session_queries(user_session):
    return [{
        constants.session_query_tasks: query.get_tasks(),
        constants.session_query_user_query_msg: query.get_user_query_msg()
    } for query in user_session.queries_list]


def get_operators_descriptions():
    operators_descriptions_str = ""
    for operator in operators_handler_module.op_functions:
        operators_descriptions_str += (
                "- " + operators_handler_module.op_functions[operator]["operator_name"] + " --> "
                + "(" + operator + ") " + operators_handler_module.op_functions[operator]["description"] + "\n")

    return operators_descriptions_str


def list_operators():
    return [str(key) for key in operators_handler_module.op_functions.keys()]


def plan_level_0(user_objective, user_session, session_query):
    # Construct planner request
    planner_messages = []
    template_path = "resources/planner_level0_prompt.txt"
    session_summary = summarize_session_queries(user_session)
    session_summary_str = json.dumps(session_summary, indent=2) if len(session_summary) > 0 else ""
    prompt_text = jinja_utils.load_template(template_path, {
        "session_summary": session_summary_str,
        "service_name": operators_handler_module.group_name,
        "op_descriptions": get_operators_descriptions(),
        "operators": list_operators()
    })
    planner_messages.append({"role": "system", "content": prompt_text})
    planner_messages.append({"role": "user", "content": f"From {operators_handler_module.group_name} Operator: The user is asking: " + user_objective})
    planner_messages.append({"role": "assistant", "content": "The full plan containing all required tasks and one or more UI Operator in JSON:"})
    session_query.set_pending_agent_communications(component=constants.session_query_leve0_plan, sub_component=constants.Request, value=copy.deepcopy(planner_messages))

    # Construct planner response
    cached_level0_plan_response = session_query.get_cached_agent_communications_planner_response(planner_messages)
    if cached_level0_plan_response is not None:
        planned_tasks = cached_level0_plan_response
    else:
        planned_tasks = json.loads(llm_GPT.run(planner_messages, planner_llm_models_list))
    session_query.set_pending_agent_communications(component=constants.session_query_leve0_plan, sub_component=constants.Response, value=copy.deepcopy(planned_tasks))

    # Parse tasks
    if constants.session_query_tasks in planned_tasks:
        tasks = planned_tasks[constants.session_query_tasks]
    elif isinstance(planned_tasks, list):
        tasks = planned_tasks
    else:
        raise UnknownCommandError(f"Unexpected format for the tasks: {planned_tasks}")

    logger.system_message("Got the following plan from the planning agent:")
    logger.print_tasks(tasks)

    return tasks


def plan_level_1(query_str, tasks):
    for i in range(0, len(tasks)):
        task = tasks[i]

        if task[constants.Operator] in operators_handler_module.op_functions:  # None of the current operators requires phase 1 planning
            continue

        prompt_text = gpt_task_processor.get_command_prompt_from_task(query_str, tasks, i, "PLANNER")

        json_str = llm_GPT.run([
            {"role": "system", "content": prompt_text},
            {"role": "assistant", "content": "JSON:\n"}],
            planner_llm_models_list)

        planned_tasks = json.loads(json_str)

        if constants.session_query_tasks in planned_tasks:
            task[constants.SubTasks] = planned_tasks[constants.session_query_tasks]

        elif isinstance(planned_tasks, list):
            task[constants.SubTasks] = planned_tasks

        else:
            raise UnknownCommandError(f"Unexpected format for the tasks: {planned_tasks}")

        logger.system_message("Got the following plan from the planning agent:")
        logger.print_tasks(planned_tasks)
        task[constants.SubTasks] = planned_tasks

    return tasks
