import asyncio
import json
import uuid
import warnings
import pandas as pd
from configs import constants
from handlers import receive_and_route_user_request, session_handler
from handlers.predefined_query_handler import create_user_query_tuple


def construct_new_session():
    chat_id = uuid.uuid4()
    return session_handler.get_or_create_session(chat_id)


def extract_query_bv_columns(insight_columns):
    split_parts = insight_columns[0]["name"].split(".")
    if len(split_parts) < 3:
        return None, None, None
    business_schema = split_parts[0]
    business_view = split_parts[1]
    columns_list = []
    for column in insight_columns:
        column_name = column["name"].split(".")
        if column_name[0] != business_schema and column_name[1] != business_view:
            return None, None, None
        columns_list.append(column_name[2])
    return business_schema, business_view, columns_list


def extract_actual_bv(result):
    schema_name = result[0]["schema_name"]
    view_name = result[0]["view_name"]
    view_columns = []
    columns = json.loads(result[0]["view_columns"].replace("'", "\""))
    for col in columns:
        view_columns.append(col["name"])
    return schema_name, view_name, view_columns


async def get_query_bv_from_copilot(user_query_msg):
    user_query_obj = create_user_query_tuple(user_query_msg, {
        "level0_plan": {
            "response": {
                "tasks": [
                    {
                        "id": 1,
                        "name": "Find Business View",
                        "goal_and_purpose": "Find the most relevant Business View to query",
                        "operator": "BusinessViewFinderOp",
                        "status": "TODO",
                        "depends_on_output_of": [],
                        "result": ""
                    }
                ]
            }
        },
        "operators": [
            {
                "command": "",
                "result": ""
            }
        ]
    })
    session = construct_new_session()
    async for result in receive_and_route_user_request.async_run_planning_loop(user_query_obj, session):
        last_tasks_update = result[constants.session_query_tasks]
    return extract_actual_bv(last_tasks_update[0]["result"])


def generate_queries_to_bv_table(metadata):
    queries = metadata["UserQuery"]
    insights_columns = metadata["InsightColumns"]
    columns = ["UserQuery", "Expected_Business_Schema", "Expected_Business_View", "Expected_Business_Columns", "Actual_Business_Schema", "Actual_Business_View", "Actual_Business_Columns"]
    queries_to_bv_df = pd.DataFrame(columns=columns)
    for index in range(len(queries)):
        current_insight_columns = json.loads(insights_columns[index].replace("'", "\""))
        current_query = queries[index]
        if str(current_query) != "nan" and len(current_insight_columns) != 0:
            expected_business_schema, expected_business_view, expected_columns_list = extract_query_bv_columns(current_insight_columns)
            if expected_business_schema:
                actual_schema_name, actual_view_name, actual_view_columns = asyncio.run(get_query_bv_from_copilot(current_query))
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=FutureWarning)
                    queries_to_bv_df = queries_to_bv_df.append({"UserQuery": queries[index], "Expected_Business_Schema": expected_business_schema,
                                                                "Expected_Business_View": expected_business_view, "Expected_Business_Columns": expected_columns_list,
                                                                "Actual_Business_Schema": actual_schema_name, "Actual_Business_View": actual_view_name, "Actual_Business_Columns": actual_view_columns},
                                                               ignore_index=True)
    return queries_to_bv_df
