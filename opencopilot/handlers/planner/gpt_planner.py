import copy
import json
import importlib
import opencopilot.utils.logger as logger
from opencopilot.configs import constants
from opencopilot.handlers.executor import gpt_task_processor
from opencopilot.configs.env import operators_path
from opencopilot.utils import jinja_utils
from opencopilot.utils.exceptions import UnknownCommandError
from opencopilot.utils.langchain import llm_GPT

operators_handler_module = importlib.import_module(operators_path + ".operators_handler")
planner_llm_models_list = [constants.LLMModelPriority.primary_model.value, constants.LLMModelPriority.secondary_model.value]


def get_next_todo_task_index(tasks_list):
    i = 0
    for task in tasks_list:
        if task[constants.Status] == constants.TODO:
            return i
        i += 1

    return -1


def summarize_session_queries(user_session, max_history_size=2000):
    """
    This function generates a summary of a user's session queries.
    
    The summary is represented as a list of dictionaries, each dictionary containing a shortened version 
    of a user's query and the corresponding result. The final query is always fully included, 
    while the remaining queries are included in a shortened form until they fill up the remaining 
    percentage of the total allowed history size.
    
    The function uses the following percentages to determine how much of the total history size 
    each component can take up:
    - The final query message: 30%
    - The final query result: 30%
    - All remaining queries and results: 40% (each individual query or result can take up to 5%)
    
    If a query's message and result combined would exceed the remaining history size, 
    that query is not included in the summary.

    Args:
      user_session (MockUserSession): The user session containing the queries to summarize.
      max_history_size (int, optional): The maximum allowed size of the history. Default is 2000.

    Returns:
      List[Dict[str, str]]: The summary of the user's session queries.
    """

    QUERY_PERCENTAGE = 0.3
    RESULT_PERCENTAGE = 0.3
    REMAINING_PERCENTAGE = 0.4
    INDIVIDUAL_PERCENTAGE = 0.05

    def shorten_text(text, max_length):
        return text if len(text) <= max_length else text[:max_length-3] + "..."

    summary = []
    temp_summary = []

    # Process the last query first
    last_query = user_session.queries_list[-1] if user_session.queries_list else None
    if last_query:
        last_query_msg = shorten_text(last_query.get_user_query_msg(), int(max_history_size * QUERY_PERCENTAGE))
        last_query_result = shorten_text(last_query.get_tasks()[-1]['result'] if last_query.get_tasks() else '', int(max_history_size * RESULT_PERCENTAGE))

        summary.append({
          "user_query_msg": last_query_msg,
          "reply": last_query_result
        })

    # Process the remaining queries
    remaining_chars = int(max_history_size * REMAINING_PERCENTAGE)
    remaining_queries = user_session.queries_list[:-1][::-1]  # Reverse the order to prioritize recent queries

    for query in remaining_queries:
        query_msg = shorten_text(query.get_user_query_msg(), int(max_history_size * INDIVIDUAL_PERCENTAGE))
        query_result = shorten_text(query.get_tasks()[-1]['result'] if query.get_tasks() else '', int(max_history_size * INDIVIDUAL_PERCENTAGE))

        if len(query_msg) + len(query_result) <= remaining_chars:
            remaining_chars -= len(query_msg) + len(query_result)

            # Prepend the query since we're processing in reverse order
            temp_summary.insert(0, {
              "user_query_msg": query_msg,
              "reply": query_result
            })

    # Concatenate the results, preserving the original order
    summary = temp_summary + summary

    return summary

def get_operators_info(context):
    if context is not None:
        operators = operators_handler_module.op_functions_resolver(context)
        operators_keys = operators
    else:
        operators = operators_handler_module.op_functions
        operators_keys = [str(key) for key in operators_handler_module.op_functions.keys()]

    operators_descriptions_str = ""
    for operator in operators:
        operators_descriptions_str += (
                "- " + operators_handler_module.op_functions[operator]["operator_name"] + " --> "
                + "(" + operator + ") " + operators_handler_module.op_functions[operator]["description"] + "\n")

    return operators_keys, operators_descriptions_str


def plan_level_0(user_objective, user_session, session_query, consumption_tracker):
    # Construct planner request
    planner_messages = []
    template_path = "resources/planner_level0_prompt.txt"
    session_summary = summarize_session_queries(user_session)
    session_summary_str = json.dumps(session_summary, indent=2) if len(session_summary) > 0 else ""

    context = None
    try:
        context = session_query.get_context()
    except AttributeError:
        print("Context isn't provided!")

    operators_names, operators_descriptions_str = get_operators_info(context)
    prompt_text = jinja_utils.load_template(template_path, {
        "session_summary": session_summary_str,
        "service_name": operators_handler_module.group_name,
        "op_descriptions": operators_descriptions_str,
        "operators": operators_names
    })
    planner_messages.append({"role": "system", "content": prompt_text})
    planner_messages.append({"role": "user", "content": f"From {operators_handler_module.group_name} Operator: The user is asking: " + user_objective})
    planner_messages.append({"role": "assistant", "content": "The full plan containing all required tasks and one or more UI Operator in JSON:"})
    session_query.set_pending_agent_communications(component=constants.session_query_leve0_plan, sub_component=constants.Request, value=copy.deepcopy(planner_messages))

    # Construct planner response
    consumption_tracking = None
    cached_level0_plan_response = session_query.get_cached_agent_communications_planner_response(planner_messages)
    if cached_level0_plan_response is not None:
        planned_tasks = cached_level0_plan_response
    else:
        planned_tasks, consumption_tracking = llm_GPT.run(planner_messages, planner_llm_models_list)
        planned_tasks = json.loads(planned_tasks)

    consumption_tracker.set_planner_consumption(consumption_tracking, "level 0")

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
