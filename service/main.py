import json
from typing import Dict, Any, List, Union

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from configs import constants
from handlers import receive_and_route_user_request
from handlers import session_handler
from handlers.predefined_query_handler import create_user_query_tuple

app = FastAPI()

# WARNING: Not a production code, because CORS of null is a security hole, remove before production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # allows CORS from local files
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserQuery(BaseModel):
    query_message: str


class Task(BaseModel):
    id: int
    name: str
    goal_and_purpose: str
    operator: str
    status: str
    depends_on_output_of: List[int]
    detailed_purpose: str
    result: Union[List[Any], Dict[str, Any], str]


class Response(BaseModel):
    result: str
    context: str
    tasks: List[Task]


@app.get("/async_query")
@app.post("/async_query")
async def handle_async_query(request: Request):
    chat_id = request.path_params.get("chat_id")
    query_string = request.query_params.get("query_string")
    predefined_obj = {}
    if request.method == "POST":
        # To include a predefined_obj, send it in the post request body
        predefined_obj = await request.json()

    user_query_obj = create_user_query_tuple(query_string, predefined_obj)

    session = session_handler.get_or_create_session(chat_id)

    async def generate_events():
        last_tasks_update = None
        last_session_query = None
        async for result in receive_and_route_user_request.async_run_planning_loop(user_query_obj, session):
            yield {"data": json.dumps(result[constants.session_query_tasks], indent=2)}
            last_tasks_update = result[constants.session_query_tasks]
            last_session_query = result[constants.session_query]
            last_session_query.set_tasks(last_tasks_update)
            last_session_query.set_store("SOME_DUMMY_STORE")

        session.update_session(last_session_query)

    response = EventSourceResponse(generate_events())
    response.headers['X-Accel-Buffering'] = 'no'
    return response


@app.get("/query")
async def handle_query(chat_id: str = None, query_string: str = "", predefined_obj: str = ""):
    user_query_obj = create_user_query_tuple(query_string, predefined_obj)

    session = session_handler.get_or_create_session(chat_id)
    last_tasks_update = None
    last_session_query = None
    for result in receive_and_route_user_request.async_run_planning_loop(user_query_obj, session):
        last_tasks_update = result[constants.session_query_tasks]
        last_session_query = result[constants.session_query]
        last_session_query.set_tasks(last_tasks_update)
        last_session_query.set_store("SOME_DUMMY_STORE")

    session.update_session(last_session_query)
    return last_tasks_update
