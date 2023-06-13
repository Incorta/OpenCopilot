from configs.env import incorta_api_access_token, incorta_url
from operators.incorta.api_helpers import post
from utils import logger
from utils.exceptions import APIFailureException


def get_business_schemas():
    logger.system_message("Getting schemas from incorta")
    url = f'{incorta_url}/incorta/api/v2/schema/list?schemaType=BUSINESS'

    def json_to_res_array(json_result):
        schemas_details = json_result['schemasDetails']

        return [
            {
                'id': schema['schemaID'],
                'name': schema['schemaName'],
                'description': schema['schemaDescription']
            }
            for schema in schemas_details
        ]

    result = post.run_paginated_get_all(url, incorta_api_access_token, json_to_res_array)

    logger.system_message("Got result from Incorta:")
    logger.operator_response(result)

    return result


def get_view_columns_basic_info(columns):
    return [
        {
            'name': column['name'],
            'label': column['label'],
            'description': column['description']
        }
        for column in columns]


def get_schema_views(schema_name, include_columns=False):
    url = f'{incorta_url}/incorta/api/v2/schema/{schema_name}/list'

    logger.system_message(f"Getting schemas tables from incorta using URL {url}")

    def json_to_res_array(json_result):
        tables_details = json_result['viewsDetails']

        return [
            {
                'name': table['name'],
                **({'columns': get_view_columns_basic_info(table['columns'])} if include_columns else {})
            }
            for table in tables_details
        ]

    result = post.run_paginated_get_all(url, incorta_api_access_token, json_to_res_array)

    logger.system_message("Got result from Incorta:")
    logger.operator_response(result)

    return result


def get_business_view_columns(schema_name, table_name):
    if "." in table_name:
        table_name = table_name.split(".")[1]

    logger.system_message(f"Getting business view's columns"
                          f"from incorta for schema.view [{schema_name}].[{table_name}]")

    views = get_schema_views(schema_name, True)

    for view in views:
        if view['name'] == table_name:
            return view['columns']

    names = [view['name'] for view in views]

    raise APIFailureException(f"Unknown {schema_name}.{table_name}, given list: {names}")
