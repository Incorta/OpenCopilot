import requests

from configs import env

INCORTA_URL = env.incorta_url


def incorta_login(host, user, pw, tenant):
    parameters = {
        "user": user,
        "pass": pw,
        "tenant": tenant
    }
    error_msg = "Error while logging in to the incorta instance"
    response = send_request("POST", host + "/incorta/authservice/login", parameters, None, None, None, None,
                            error_msg)
    jsessionid = response.cookies
    response = send_request("GET", host + "/incorta/service/user/isLoggedIn", None, None, None, None,
                            jsessionid, error_msg)
    token = response.json()["accessToken"]
    xsrf_token = response.cookies.get('XSRF-TOKEN')
    return token, jsessionid, xsrf_token


def send_request(request_type, url, params, headers, files, data, cookies, error_msg):
    s = requests.session()
    response = None
    try:
        if request_type == "POST":
            response = s.post(url, params=params, headers=headers, files=files, data=data, cookies=cookies)
        elif request_type == "GET":
            response = s.get(url, params=params, headers=headers, files=files, data=data, cookies=cookies)
    except requests.exceptions.RequestException as e:
        print(e)
    if response.status_code != 200:
        print(error_msg + ", status_code:" + str(response.status_code) + ", response_message: " + response.json()["message"])
    return response


def get_dashboards(new_dashboard_id, token, jsessionid):
    headers = {
        "authorization": "Bearer " + token,
        "content-type": "application/json"
    }
    dashboards_url = INCORTA_URL + f"/incorta/bff/v1/dashboards?{new_dashboard_id}viewMode=All&sortBy=alphabeticalAsc"
    dashboards = send_request("GET", dashboards_url, None, headers, None, None, jsessionid, "Error while getting dashboards").json()['dashboards']
    return dashboards


def get_folders(new_folder_id, token, jsessionid):
    headers = {
        "authorization": "Bearer " + token,
        "content-type": "application/json"
    }
    folders_url = INCORTA_URL + f"/incorta/bff/v1/folders?{new_folder_id}viewMode=All"
    folders = send_request("GET", folders_url, None, headers, None, None, jsessionid, "Error while getting folders").json()['folders']
    return folders


def get_insight_sql(insight_definition, token, jsessionid, xsrf_token):
    formatted_insight_definition = "<report><layout> " + insight_definition[insight_definition.index(">") + 1:].replace('\"', '\\"') + " </layout> </report>"
    headers = {
        "authorization": "Bearer " + token,
        "content-type": "application/json",
        "x-xsrf-token": xsrf_token
    }
    insight_sql_url = INCORTA_URL + f"/incorta/service/catalogreport/insightToSql"
    data = "{\"code\":\"" + formatted_insight_definition + "\",\"prompts\":\"{}\",\"comp_state\":\"{}\"}"
    insight_sql = send_request("POST", insight_sql_url, None, headers, None, data, jsessionid, "Error while getting insight sql").json()["sql"]
    return insight_sql


def get_insight_definition(dashboard_guid, layout_guid, insight_guid, token, jsessionid):
    headers = {
        "authorization": "Bearer " + token,
        "content-type": "application/json"
    }
    data = "{\"prompts\": [], \"resolveVariables\": true}"

    insight_def_url = INCORTA_URL + f"/incorta/bff/v1/dashboards/{dashboard_guid}/layouts/{layout_guid}/insights/{insight_guid}"
    insight_definition = send_request("POST", insight_def_url, None, headers, None, data, jsessionid, "Error while getting insights definitions").text
    return insight_definition


def get_dashboard_definition(guid, token, jsessionid):
    headers = {
        "authorization": "Bearer " + token,
        "content-type": "application/json"
    }
    dashboard_def_url = INCORTA_URL + f"/incorta/bff/v1/dashboards/{guid}"
    dashboard_definition = send_request("GET", dashboard_def_url, None, headers, None, None, jsessionid, "Error while getting dashboards definitions")
    return dashboard_definition


# For Incorta releases >= 2023.4.1
def get_insight_dependencies(insight_ids_list, token, jsessionid, xsrf_token):
    headers = {
        "authorization": "Bearer " + token,
        "content-type": "application/json",
        "x-xsrf-token": xsrf_token
    }
    data = "{\"entityIdentifiers\": [\"" + insight_ids_list + "\"], \"multiLevel\": false, \"downstream\": false}"
    dependencies_url = INCORTA_URL + "/incorta/bff/v1/dependencies"
    insight_dependencies = send_request("POST", dependencies_url, None, headers, None, data, jsessionid, "Error while getting insights dependencies").json()['dependencies']
    return insight_dependencies
