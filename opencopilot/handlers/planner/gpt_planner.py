import copy
import json
import importlib
import opencopilot.utils.logger as logger
from opencopilot.configs import constants
from opencopilot.configs.ai_providers import get_planner_prompt_file_path
from opencopilot.configs.env import operators_path
from opencopilot.utils import jinja_utils
from opencopilot.utils.exceptions import UnknownCommandError
from opencopilot.utils.langchain import llm_GPT
from opencopilot.utils.langchain.llm_GPT import resolve_llm_model
from opencopilot.utils.llm_evaluator import evaluate_llm_reply

operators_handler_module = importlib.import_module(operators_path + ".operators_handler")
planner_llm_models_list = [constants.LLMModelPriority.primary_model.value, constants.LLMModelPriority.secondary_model.value]


def get_next_todo_task_index(tasks_list):
    i = 0
    for task in tasks_list:
        if task[constants.Status] == constants.TODO:
            return i
        i += 1

    return -1


def resolve_tasks(tasks_list):
    import re
    # Create a mapping of ids to results for easier access
    task_results = {}
    for task in tasks_list:
        if isinstance(task['result'], str):
            task_results[task['id']] = task['result']
        elif isinstance(task['result'], dict):
            task_results[task['id']] = str(task['result'])
    # Iterate over tasks_list
    for task in tasks_list:
        # Find all taskID references in the result string
        if "message" in task['result']:
            result_message = task['result']['message']

            # Find all occurrences of @taskID in the result_message
            for match in re.finditer(r'@task(\d+)', result_message):
                id = match.group(1)
                if int(id) in task_results:
                    # Replace each reference with the corresponding task result
                    result_message = result_message.replace(
                        '@task' + id, task_results[int(id)])

            task['result']['message'] = result_message

    return tasks_list


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
        return text if len(text) <= max_length else text[:max_length - 3] + "..."

    summary = []
    temp_summary = []

    # Process the last query first
    last_query = user_session.queries_list[-1] if user_session.queries_list else None
    if last_query:
        last_query_msg = shorten_text(last_query.get_user_query_msg(), int(max_history_size * QUERY_PERCENTAGE))
        resolved_tasks = resolve_tasks(last_query.get_tasks())
        last_query_result = shorten_text(resolved_tasks[-1]['result'] if last_query.get_tasks() else '', int(max_history_size * RESULT_PERCENTAGE))

        summary.append({
            "user_query_msg": last_query_msg,
            "reply": last_query_result
        })

    # Process the remaining queries
    remaining_chars = int(max_history_size * REMAINING_PERCENTAGE)
    remaining_queries = user_session.queries_list[:-1][::-1]  # Reverse the order to prioritize recent queries

    for query in remaining_queries:
        query_msg = shorten_text(query.get_user_query_msg(), int(max_history_size * INDIVIDUAL_PERCENTAGE))
        resolved_tasks = resolve_tasks(query.get_tasks())
        query_result = shorten_text(resolved_tasks[-1]['result'] if query.get_tasks() else '', int(max_history_size * INDIVIDUAL_PERCENTAGE))

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


def formulate_operators_constraints(operators):
    operators_constraints_str = ""
    for operator in operators:
        if "constraints" in operators_handler_module.op_functions[operator] and operators_handler_module.op_functions[operator]["constraints"]:
            for constraint in operators_handler_module.op_functions[operator]["constraints"]:
                operators_constraints_str += "\n - " + constraint

    return operators_constraints_str


def construct_level_0_prompt(user_objective, context, user_session, model):
    session_summary = summarize_session_queries(user_session)
    session_summary = {str(i + 1): d for i, d in enumerate(session_summary)}
    session_summary_str = json.dumps(session_summary, indent=2) if len(session_summary) > 0 else ""
    operators_names, operators_descriptions_str = get_operators_info(context)
    operators_constraints = formulate_operators_constraints(operators_names)

    plan_schema = jinja_utils.load_template("resources/plan_schema.txt", {
        "service_name": operators_handler_module.service_name,
        "operators": json.dumps(operators_names)
    })
    system_content = jinja_utils.load_template(get_planner_prompt_file_path(model["ai_provider"], "system"), {
        "session_summary": session_summary_str,
        "service_name": operators_handler_module.service_name,
        "op_descriptions": operators_descriptions_str,
        "operators": operators_names,
        "plan_schema": plan_schema,
        "op_constraints": operators_constraints
    })
    user_content = jinja_utils.load_template(get_planner_prompt_file_path(model["ai_provider"], "user"), {
        "service_name": operators_handler_module.group_name,
        "user_objective": user_objective
    })

    planner_messages = [{"role": "user", "content": system_content + "\n" + user_content}]

    return planner_messages, session_summary, plan_schema


def plan_level_0(user_objective, user_session, session_query, consumption_tracker, evaluator, evaluate_response):
    model = resolve_llm_model(planner_llm_models_list)

    # Construct planner request
    planner_messages, session_summary, _ = construct_level_0_prompt(user_objective, session_query.get_context(), user_session, model)
    session_query.set_pending_agent_communications(component=constants.session_query_level0_plan, sub_component=constants.Request, value=copy.deepcopy(planner_messages))

    # Construct planner response
    cached_level0_plan_response = session_query.get_cached_agent_communications_planner_response(planner_messages)
    if cached_level0_plan_response is not None:
        planned_tasks = cached_level0_plan_response
    else:
        planned_tasks, consumption_tracking, _ = llm_GPT.run(planner_messages, model)
        consumption_tracker.add_consumption(consumption_tracking, constants.planner, "level 0")
        if evaluate_response:
            evaluation, evaluation_consumption_tracking = evaluate_llm_reply(planner_messages, planned_tasks)
            evaluator.add_llm_evaluation(evaluation, constants.planner, "level 0")
            consumption_tracker.add_consumption(evaluation_consumption_tracking, constants.planner, "* Evaluation")

    try:
        planned_tasks = json.loads(planned_tasks)
    except:
        pass

    session_query.set_pending_agent_communications(component=constants.session_query_level0_plan, sub_component=constants.Response, value=copy.deepcopy(planned_tasks))

    # Parse tasks
    if constants.session_query_tasks in planned_tasks:
        tasks = planned_tasks[constants.session_query_tasks]
    elif isinstance(planned_tasks, list):
        tasks = planned_tasks
    else:
        raise UnknownCommandError(f"Unexpected format for the tasks: {planned_tasks}")

    logger.system_message("Got the following plan from the planning agent:")
    logger.print_tasks(tasks)

    return tasks, session_summary
