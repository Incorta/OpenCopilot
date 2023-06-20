import ast
import json
from time import sleep

from utils import jinja_utils
from utils.open_ai import completion_3_5


def check_business_view_in_insight_cols(row):
    insight_cols = ast.literal_eval(row["InsightColumns"])
    if len(insight_cols) == 0:
        return False

    for column_obj in insight_cols:
        if "BUSINESS_VIEW" not in column_obj["type"]:
            return False
    return True


def generate_user_queries(analytics_metadata_df):
    user_queries_list = [''] * len(analytics_metadata_df.index)
    index = 0
    while index < len(analytics_metadata_df):
        row = analytics_metadata_df.iloc[index]
        user_query = ""
        print("Index: " + str(index))
        if str(row["InsightName"]) != "nan" and check_business_view_in_insight_cols(row):
            dashboard_name = row['DashboardName']
            layout_name = row['LayoutName']
            insight_name = row["InsightName"]

            prompt_text = jinja_utils.load_template("generators/user_queries/generate_user_query_prompt.txt", {
                "dashboardName": dashboard_name,
                "layoutName": layout_name,
                "insightName": insight_name
            })
            messages = [{"role": "system", "content": prompt_text}]
            try:
                user_query = completion_3_5.run(
                    messages
                )
                user_query = json.loads(user_query)['user_query']
                print(user_query)
                sleep(5)
            except Exception as e:
                print(e)
                print("Retrying Query at index: " + str(index))
                index -= 1

        user_queries_list[index] = user_query
        index += 1

    analytics_metadata_df = analytics_metadata_df.assign(UserQuery=user_queries_list)
    return analytics_metadata_df
