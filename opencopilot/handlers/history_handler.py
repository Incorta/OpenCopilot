import copy
import importlib
from collections import deque

from opencopilot.configs.constants import Operator, Result
from opencopilot.configs import constants
from opencopilot.configs.env import operators_path
from opencopilot.utils.tokens_counter import count_prompt_tokens

operators_handler_module = importlib.import_module(operators_path + ".operators_handler")
planner_llm_models_list = [constants.LLMModelPriority.primary_model.value, constants.LLMModelPriority.secondary_model.value]


def construct_summary_object(user_session):
    session_summary = {}
    try:
        session_summary = summarize_session_queries(user_session)
        session_summary = {str(i + 1): d for i, d in enumerate(session_summary)}
    except:
        pass

    return session_summary


def summarize_session_queries(user_session, max_history_size=1000):
    """
    This function generates a summary of a user's session queries using a queue-based approach.

    The summary is represented as a list of dictionaries, each containing a user's query and the corresponding result.
    The function ensures that the summary does not exceed the max_history_size by maintaining a queue of the most recent queries.

    Args:
        user_session: The user session containing the queries to summarize.
        max_history_size (int, optional): The maximum allowed size of the history. Default is 2000.

    Returns:
        List[Dict[str, str]]: The summary of the user's session queries.
    """
    summary_queue = deque()
    total_length = 0

    # Iterate through the user's session queries except the last one
    for query in user_session.queries_list[:-1]:
        query_msg = query.get_user_query_msg()
        tasks = query.get_tasks()

        # Check if there are any tasks
        if tasks:
            last_task = tasks[-1]
            operator = last_task.get(Operator, "")
            result = last_task.get(Result, "")
            process_result_for_summary = operators_handler_module.op_functions[operator].get("executor_args").get("process_result_for_summary", None)
            # Check if there's a function to process the result
            if process_result_for_summary:
                query_result = process_result_for_summary(copy.deepcopy(tasks))

            # Use the raw result if no processing function is found
            else:
                query_result = result

        # Default to an empty string if there are no tasks
        else:
            query_result = ""

        query_length = count_prompt_tokens(query_msg + query_result)

        # Add the new query and result to the queue
        summary_queue.append({
            "user_query_msg": query_msg,
            "reply": query_result
        })
        total_length += query_length  # Update the total length counter

        # If the total length exceeds max_history_size, remove the oldest queries
        while total_length > max_history_size and summary_queue:
            oldest_query = summary_queue.popleft()
            total_length -= count_prompt_tokens(oldest_query["user_query_msg"] + oldest_query["reply"])

    # Convert the deque to a list before returning
    return list(summary_queue)