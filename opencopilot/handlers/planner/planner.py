import copy
import json
import importlib

from opencopilot.configs import constants
from opencopilot.configs.ai_providers import get_planner_prompt_file_path
from opencopilot.configs.constants import LLMModelPriority
from opencopilot.configs.env import operators_path
from opencopilot.handlers.history_handler import construct_summary_object
from opencopilot.utils import jinja_utils
from opencopilot.utils.exceptions import UnknownCommandError
from opencopilot.utils.langchain import llm_GPT
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


def get_operators_info(context):
    if context is not None:
        operators = operators_handler_module.op_functions_resolver(context)
    else:
        operators = operators_handler_module.op_functions

    operators_descriptions_str = ""
    for operator_key, operator_obj in operators.items():
        operators_descriptions_str += (
                "- " + operator_obj["operator_name"] + " --> "
                + "(" + operator_key + ") " + operator_obj["description"] + "\n")

    return operators, operators_descriptions_str


def formulate_operators_constraints(operators):
    operators_constraints_str = ""
    for operator in operators:
        if "constraints" in operators[operator] and operators[operator]["constraints"]:
            for constraint in operators[operator]["constraints"]:
                operators_constraints_str += "\n - " + constraint

    return operators_constraints_str


def construct_level_0_prompt(user_objective, context, session_summary_str, model):
    supported_operators, operators_descriptions_str = get_operators_info(context)
    operators_constraints = formulate_operators_constraints(supported_operators)

    plan_schema = jinja_utils.load_template("resources/plan_schema.txt", {
        "service_name": operators_handler_module.service_name,
        "operators": supported_operators.keys()
    })
    system_content = jinja_utils.load_template(get_planner_prompt_file_path(model.provider, "system"), {
        "session_summary": session_summary_str,
        "service_name": operators_handler_module.service_name,
        "op_descriptions": operators_descriptions_str,
        "operators": supported_operators.keys(),
        "plan_schema": plan_schema,
        "op_constraints": operators_constraints
    })
    user_content = jinja_utils.load_template(get_planner_prompt_file_path(model.provider, "user"), {
        "service_name": operators_handler_module.group_name,
        "user_objective": user_objective
    })

    planner_messages = [
        {
            "role": "user",
            "content": system_content + user_content
        }
    ]

    return planner_messages, plan_schema, supported_operators


def plan_level_0(user_objective, user_session, session_query, consumption_tracker, evaluator, evaluate_response, copilot_configs):
    model = copilot_configs.llm_models[LLMModelPriority.primary_model.value]

    session_summary = construct_summary_object(user_session)
    session_summary_str = json.dumps(session_summary, indent=2) if len(session_summary) > 0 else ""

    # Construct planner request
    planner_messages, _, supported_operators = construct_level_0_prompt(user_objective, session_query.get_context(), session_summary_str, model)
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

    return tasks, session_summary, supported_operators
