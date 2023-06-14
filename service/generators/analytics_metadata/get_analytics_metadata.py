import warnings
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from generators.analytics_metadata.incorta_client import get_folders, get_dashboards, get_insight_definition, get_insight_sql, get_dashboard_definition, get_insight_dependencies
import pandas as pd

dashboards_guids = list()
folders_ids = list()

columns = ['DashboardGUID', 'DashboardName', 'LayoutGUID', 'LayoutName', 'InsightGUID', 'InsightName', 'InsightType', 'InsightDescription', 'InsightColumns', 'InsightSQL']
metadata_df = pd.DataFrame(columns=columns)


def construct_analytics_metadata_table(token, jsessionid, xsrf_token):
    get_dashboards_guids(token, jsessionid)
    explore_dashboards(token, jsessionid, xsrf_token)
    save_metadata_df_to_file()


def get_dashboards_guids(token, jsessionid, new_folder_id="", new_dashboard_id=""):
    folders = get_folders(new_folder_id, token, jsessionid)
    dashboards = get_dashboards(new_dashboard_id, token, jsessionid)

    # Collect dashboards GUIDs
    for dashboard in dashboards:
        dashboards_guids.append(dashboard['guid'])

    for folder in folders:
        # Collect folders ids
        folders_ids.append(folder['id'])

    if len(folders_ids) == 0:
        # No more folders in the tree
        return

    for folder_id in folders_ids:
        new_folder_id = f"id={folder_id}&"
        new_dashboard_id = f"folderId={folder_id}&"
        folders_ids.remove(folder_id)

        get_dashboards_guids(token, jsessionid, new_folder_id=new_folder_id, new_dashboard_id=new_dashboard_id)


def extract_insights_metadata(dashboard_definition, token, jsessionid, xsrf_token):
    global metadata_df

    dashboard_guid = dashboard_definition["guid"]
    dashboard_name = dashboard_definition["name"]
    for layout in dashboard_definition["layouts"]:
        layout_guid = layout["layoutGuid"]
        layout_name = layout["name"]
        for container in layout["containers"]:
            for component in container["components"]:
                insight_guid = component["id"]
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=MarkupResemblesLocatorWarning)
                    insight_name = BeautifulSoup(component["name"], features="html.parser").get_text()
                insight_type = component["type"] + ": " + component["insightType"] if "insightType" in component else component["type"]
                insight_description = component["description"]
                insight_definition = get_insight_definition(dashboard_guid, layout_guid, insight_guid, token, jsessionid)
                try:
                    insight_sql = get_insight_sql(insight_definition, token, jsessionid, xsrf_token)
                except Exception:
                    insight_sql = ""
                insight_id = dashboard_guid + "/" + layout_guid + "/" + insight_guid
                insights_first_level_dependencies = get_insight_dependencies(insight_id, token, jsessionid, xsrf_token)[insight_id]
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=FutureWarning)
                    metadata_df = metadata_df.append({'DashboardGUID': dashboard_guid, 'DashboardName': dashboard_name, 'LayoutGUID': layout_guid, 'LayoutName': layout_name,
                                                      'InsightGUID': insight_guid, 'InsightName': insight_name, 'InsightType': insight_type, 'InsightDescription': insight_description,
                                                      'InsightColumns': insights_first_level_dependencies, 'InsightSQL': insight_sql}, ignore_index=True)


def explore_dashboards(token, jsessionid, xsrf_token):
    for guid in dashboards_guids:
        dashboard_definition = get_dashboard_definition(guid, token, jsessionid)
        extract_insights_metadata(dashboard_definition.json(), token, jsessionid, xsrf_token)


def save_metadata_df_to_file():
    metadata_df.to_csv('analytics_metadata_table.csv')
