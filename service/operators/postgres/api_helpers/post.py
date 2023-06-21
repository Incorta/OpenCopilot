import requests
from utils.exceptions import APIFailureException
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL verification
requests.packages.urllib3.disable_warnings()


def run_paginated_get_all(url, token, res_transformer):
    # Set up the headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Set up the request body
    limit = 100
    offset = 0
    request_body = {
        "limit": limit,
        "offset": offset,
    }

    result_array = []

    while True:
        response = requests.post(url, headers=headers, json=request_body, verify=False)

        if response.status_code == 200:
            new_list = res_transformer(response.json())
            result_array.extend(new_list)

            # Check if there are more schemas to fetch
            if len(new_list) < limit:
                break

            # Update the offset for the next request
            offset += limit
            request_body["offset"] = offset
        else:
            raise APIFailureException(f'Failed to get results from incorta with url: {url}. Response:\n{response.text}')
            break

    return result_array


def run_plain_response(url, token):
    # Set up the headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    while True:
        response = requests.get(url, headers=headers, verify=False)

        if response.status_code == 200:
            return response.text
        else:
            raise APIFailureException(f'Failed to get results from incorta with url: {url}. Response:\n{response.text}')
            break

    return result_array
