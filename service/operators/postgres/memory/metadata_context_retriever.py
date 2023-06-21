import chromadb
from chromadb.config import Settings
import json
import time
from chromadb.utils import embedding_functions

from operators.postgres.api_common.schemas import get_table_columns
from utils import logger
from operators.postgres.api_common import schemas
from utils.open_ai import completion_3_5
from utils import network
from configs.env import openai_text_ada_api_key, enable_ad_hoc_views_indexing

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_text_ada_api_key,
    model_name="text-embedding-ada-002"
)

# setup Chroma in-memory, for easy prototyping. Can add persistence easily!
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=".chromadb/"
))

use_transient_chroma = False

views_collection = client.get_or_create_collection(name="tables_transient") \
    if use_transient_chroma else client.get_or_create_collection(name="tables", embedding_function=openai_ef)


def generate_table_summary(view):
    schema_info = f"viewName: {view['name']}\n" \
                  f"viewInfo: {get_trimmed_table_str(view, 3500)}"

    messages = [{"role": "system", "content": """
    We've a DB View, with info as follows:
    """ + schema_info[:3700] +
                 """
    Summarize the view info and its columns in 200 chars, as keywords to use with embedding DBs.
    Reply with summary comma-separated keywords in a python directly with no additional text. 
                 """
                 }]

    response = network.retry(lambda: completion_3_5.run(messages, parse_as_json=False))

    logger.system_message("Got summary from GPT:")
    logger.operator_response(response)

    return response


def get_trimmed_table_str(table, max_len):
    view_str = json.dumps(table)

    # Perform binary search to find the right number of columns to be included
    low = 0
    high = len(table['columns'])
    cur_size = (low + high) // 2

    while low < high:
        view_str = json.dumps({
            'name': table['name'],
            'columns': table['columns'][:cur_size]
        })

        if len(view_str) > max_len:
            high = cur_size - 1
        else:
            low = cur_size + 1
        cur_size = (low + high) // 2

    return view_str[:max_len]


def get_top_relevant_schemas_results(n, query, force_enable_ad_hoc_views_indexing=False):
    if force_enable_ad_hoc_views_indexing or enable_ad_hoc_views_indexing:
        all_schemas = schemas.get_schemas()

        for i in range(0, len(all_schemas)):
            schema = all_schemas[i]
            schema_id = 2

            schema_name = schema

            # if schema['name'] != "OrderManagementTableau":
            #     continue

            schema_tables = schemas.get_schema_tables(schema_name, True)

            for j in range(0, len(schema_tables)):
                table_name = schema_tables[j]
                # TODO handle chroma_db
                chroma_id = f"schema_{schema_name}_view_{table_name}" #Assume schema name and table name can compose composite key
                prev_embedding = views_collection.get(ids=[chroma_id])

                if len(prev_embedding['ids']) > 0:
                    logger.system_message(f'Found previous embedding for view in schema: {schema_name} id: {chroma_id}')
                    continue

                logger.trace(f"Processing schema: {i}/{len(all_schemas)}, view: {j}/{len(schema_tables)}")


                view_doc = f"schemaName: {schema_name}\n" \
                           f"tableName: {table_name}\n" \

                network.retry(lambda: views_collection.add(
                    documents=[view_doc],
                    metadatas=[{"type": "table", "schema_name": schema_name,
                                "tableName": f"{table_name}", "table_columns": f"{str(get_table_columns(schema_name, table_name))}"}],
                    ids=[chroma_id]
                ))

                time.sleep(1)  # Wait for 2 seconds before attempting the next view, to avoid rate limiter

    logger.system_message("Query history for relevant results, with query: " + query)

    return views_collection.query(
        query_texts=[query],
        n_results=n
    )


def get_top_relevant_table(n, query):
    results = get_top_relevant_schemas_results(n, query)
    # metadatas = results['metadatas'][0]
    #
    # result = [
    #     {
    #         "id": schema['schema_id'],
    #         "schema_name": schema['schema_name'],
    #         "view_name": schema['view_name'],
    #         "view_columns": schema['view_columns']
    #     }
    #     for schema in metadatas]
    #
    # logger.system_message("Got relevant schemas:")
    # logger.operator_response(result)

    return results
