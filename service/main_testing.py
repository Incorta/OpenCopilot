import asyncio
import importlib
import uuid

from configs import env, constants
from handlers import session_handler, receive_and_route_user_request
from tests.E2E_tests.cached_sessions_store_handler import CachedSessionsStoreHandler


def construct_session_queries(session):
    session_queries = []
    queries_list = session.get_queries_list()
    for query in queries_list:
        session_queries.append(query.get_modified_pending_agent_communications())
    return session_queries


def construct_new_session():
    chat_id = uuid.uuid4()
    return session_handler.get_or_create_session(chat_id)


async def run_testing_framework():
    module = importlib.import_module(f"tests.E2E_tests.{env.used_incorta_env}.queries_list")

    sessions_queries_messages = module.sessions_user_queries_messages

    for session_list in sessions_queries_messages:
        session = construct_new_session()
        for query_obj in session_list:
            last_session_query = None
            async for result in receive_and_route_user_request.async_run_planning_loop(query_obj, session):
                last_tasks_update = result[constants.session_query_tasks]
                last_session_query = result[constants.session_query]
                last_session_query.set_tasks(last_tasks_update)
                last_session_query.set_store("SOME_DUMMY_STORE")

            session.update_session(last_session_query)
        if env.sessions_setting_mode:
            CachedSessionsStoreHandler().add_session_queries_to_sessions_store(construct_session_queries(session))


if __name__ == '__main__':
    asyncio.run(run_testing_framework())
