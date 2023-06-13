import json

import utils.logger as logger
from configs import env, constants
from handlers.executor import gpt_task_processor
from utils import jinja_utils
from utils.exceptions import UnknownCommandError
from utils.open_ai import completion_4


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


def plan_level_0(user_objective, user_session, session_query):
    planner_messages = []

    template_path = "resources/planner_level0_prompt.txt"
    session_summary = summarize_session_queries(user_session)

    session_summary_str = json.dumps(session_summary, indent=2) if len(session_summary) > 0 else ""

    prompt_text = jinja_utils.load_template(template_path, {
        "session_summary": session_summary_str
    })

    planner_messages.append({"role": "system", "content": prompt_text})

    planner_messages.append({"role": "user", "content": "From Incorta Operator: The user is asking: " + user_objective})
    planner_messages.append({"role": "assistant", "content": "JSON:"})

    session_query.set_pending_agent_communications(component=constants.session_query_leve0_plan, sub_component=constants.Request, value=planner_messages)

    """ If get_plan_response is enabled, retrieve plan0_response from sessions store instead of requesting it from GPT"""
    matching_level0_plan_gpt4 = None
    if env.sessions_getting_mode and (env.get_all or env.get_plan_response):
        matching_level0_plan_gpt4 = session_query.get_cached_agent_communications(component=constants.session_query_leve0_plan, sub_component=constants.Response)

    if matching_level0_plan_gpt4 is not None:
        planned_tasks = matching_level0_plan_gpt4
    else:
        planned_tasks = json.loads(completion_4.run(planner_messages))

    session_query.set_pending_agent_communications(component=constants.session_query_leve0_plan, sub_component=constants.Response, value=planned_tasks)

    tasks = []
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

        if task[constants.Operator] in [constants.BusinessViewFinderOp, constants.QueryOp, constants.UiChartOp,
                                        constants.UiTextOp]:  # None of the current operators requires phase 1 planning
            continue

        prompt_text = gpt_task_processor.get_command_prompt_from_task(tasks, i, "PLANNER")

        json_str = completion_4.run([
            {"role": "system", "content": prompt_text},
            {"role": "assistant", "content": "JSON:\n"}])

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
