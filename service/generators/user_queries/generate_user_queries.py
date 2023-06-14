import json
from utils import jinja_utils
from utils.open_ai import completion_3_5


def generate_user_queries(analytics_metadata_df):
    user_queries_list = []
    for index, row in analytics_metadata_df.iterrows():
        user_query = ""
        if str(row["InsightName"]) != "nan":
            dashboard_name = row['DashboardName']
            layout_name = row['LayoutName']
            insight_name = row["InsightName"]

            prompt_text = jinja_utils.load_template("user_queries/generate_user_query_prompt.txt", {
                "dashboardName": dashboard_name,
                "layoutName": layout_name,
                "insightName": insight_name
            })
            messages = [{"role": "system", "content": prompt_text}]

            user_query = completion_3_5.run(
                messages
            )
            user_query = json.loads(user_query)["user_query"]
        user_queries_list.append(user_query)

    analytics_metadata_df = analytics_metadata_df.assign(UserQuery=user_queries_list)
    return analytics_metadata_df
