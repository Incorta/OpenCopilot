import importlib
from opencopilot.utils import logger as logger
from opencopilot.configs import env, constants
from opencopilot.configs.env import operators_path
from opencopilot.handlers.executor import gpt_task_processor
from opencopilot.handlers.planner import gpt_planner
from controller.predefined_query_handler import validate_predefined_query
from opencopilot.tests.E2E_tests.cached_sessions_store_handler import CachedSessionsStoreHandler
from opencopilot.utils.exceptions import UnknownCommandError

operators_handler_module = importlib.import_module(operators_path + ".operators_handler")


def execute_sub_task(query_str, tasks, task_index, session_query):
    logger.system_message("Handling next task:")
    logger.operator_input(tasks[task_index])

    command = gpt_task_processor.get_command_from_task(query_str, tasks, task_index, session_query)

    session_query.set_pending_agent_communications(component=task_index, sub_component=constants.Command, value=command)

    """ If get_op_result is enabled, retrieve operator's result from sessions_store instead of handling it """
    result = None
    if env.sessions_getting_mode and (env.get_all or env.get_op_result):
        result = session_query.get_cached_agent_communications(component=task_index, sub_component=constants.Result)

    if result is None:
        if tasks[task_index][constants.Operator] in operators_handler_module.op_functions:
            result = operators_handler_module.op_functions[tasks[task_index][constants.Operator]]["handle_command"](command)
        else:
            raise UnknownCommandError(f"Unknown command: {command}")

    session_query.set_pending_agent_communications(component=task_index, sub_component=constants.Result, value=result)

    logger.system_message("Got result from operator:")
    logger.operator_response(result)

    tasks[task_index][constants.Status] = constants.DONE
    tasks[task_index][constants.Result] = result

    if constants.RequireResultSummary in command[constants.Args] and command[constants.Args][constants.RequireResultSummary]:
        tasks[task_index] = gpt_task_processor.enhance_and_finalize_task_result(command, tasks[task_index], task_index, session_query)
        session_query.set_pending_agent_communications(component=task_index, sub_component=constants.EnhancedResult, value=tasks[task_index][constants.Result])


def execute_task(query_str, tasks, task_index, session_query):
    task = tasks[task_index]
    if constants.SubTasks not in task:
        execute_sub_task(query_str, tasks, task_index, session_query)
    else:
        logger.system_message("Executing sub-task of the task: " + task["name"])
        sub_tasks = task[constants.SubTasks]
        for i in range(0, len(sub_tasks)):
            execute_sub_task(query_str, sub_tasks, i, session_query)
            i += 1

    tasks[task_index][constants.Status] = constants.DONE


async def async_run_planning_loop(query_obj, session):
    for result in run_planning_loop(query_obj, session):
        yield result


def run_planning_loop(user_query_obj, session):
    tasks = [{
        "name": "Planning",
        "goal_and_purpose": "Plan for answering the query",
        "operator": "Planner",
        "status": constants.TODO,
    }]

    user_query_msg = user_query_obj.user_query_str
    # Check that user_query_obj.predefined_agent_communication is a valid predefined query
    predefined_query = user_query_obj.predefined_agent_communication if validate_predefined_query(user_query_obj) else None

    session_query = session.Query()
    session_query.set_user_query_msg(user_query_msg)

    yield {constants.session_query_tasks: tasks, constants.session_query: session_query}

    CachedSessionsStoreHandler().initialize_cached_sessions_store()

    cached_object = CachedSessionsStoreHandler().get_query_if_exists(user_query_msg, len(session.queries_list), session)
    if predefined_query is None and env.sessions_getting_mode:
        """ If getting mode is enabled, get the query from the sessions_store, set the _cached_session_idx and use the cached object """
        predefined_query = cached_object

    if predefined_query is not None:
        session_query.set_cached_agent_communications(predefined_query)

    session_query.set_pending_agent_communications(component=constants.session_query_user_query_msg, sub_component=None, value=user_query_msg)

    initial_planned_tasks = gpt_planner.plan_level_0(user_query_msg, session, session_query)

    tasks = gpt_planner.plan_level_1(user_query_msg, initial_planned_tasks)
    logger.system_message("Enriched planned tasks:")
    logger.print_tasks(tasks)

    while True:
        yield {constants.session_query_tasks: tasks, constants.session_query: session_query}
        next_task_index = gpt_planner.get_next_todo_task_index(tasks)
        if next_task_index < 0:
            break

        execute_task(user_query_msg, tasks, next_task_index, session_query)

        yield {constants.session_query_tasks: tasks, constants.session_query: session_query}

        logger.system_message("Current tasks:")
        logger.print_tasks(tasks)

    logger.system_message("Exited the System Loop")

    return tasks, session_query
