import importlib
from collections import deque

from opencopilot.configs.env import service_utils_path
from opencopilot.utils.tokens_counter import count_prompt_tokens


service_utils_constant_module = importlib.import_module(service_utils_path + ".constants")


def construct_summary_object(user_session):
    session_summary = {}
    try:
        session_summary = summarize_session_queries(user_session)
        session_summary = {str(i + 1): d for i, d in enumerate(session_summary)}
    except:
        pass

    return session_summary


def summarize_session_queries(user_session, max_history_size=service_utils_constant_module.HISTORY_LIMIT):
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
        history = query.get_history()
        if history:
            summary_queue.append({
                                "user_query_msg": query_msg,
                                "reply": history
                            })

        # If the total length exceeds max_history_size, remove the oldest queries
        while total_length > max_history_size and summary_queue:
            oldest_query = summary_queue.popleft()
            total_length -= count_prompt_tokens(oldest_query["user_query_msg"]) + count_prompt_tokens(oldest_query["reply"])

    # Convert the deque to a list before returning
    return list(summary_queue)
