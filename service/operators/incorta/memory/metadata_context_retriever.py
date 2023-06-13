import chromadb
from chromadb.config import Settings
import json
import time
from chromadb.utils import embedding_functions
from utils import logger
from operators.incorta.api_common import schemas
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

views_collection = client.get_or_create_collection(name="business_views_transient") \
    if use_transient_chroma else client.get_or_create_collection(name="business_views", embedding_function=openai_ef)


def generate_view_summary(view):
    schema_info = f"viewName: {view['name']}\n" \
                  f"viewInfo: {get_trimmed_view_str(view, 3500)}"

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


def get_trimmed_view_str(view, max_len):
    view_str = json.dumps(view)

    # Perform binary search to find the right number of columns to be included
    low = 0
    high = len(view['columns'])
    cur_size = (low + high) // 2

    while low < high:
        view_str = json.dumps({
            'name': view['name'],
            'columns': view['columns'][:cur_size]
        })

        if len(view_str) > max_len:
            high = cur_size - 1
        else:
            low = cur_size + 1
        cur_size = (low + high) // 2

    return view_str[:max_len]


def get_top_relevant_schemas_results(n, query, force_enable_ad_hoc_views_indexing=False):
    if force_enable_ad_hoc_views_indexing or enable_ad_hoc_views_indexing:
        all_schemas = schemas.get_business_schemas()

        for i in range(0, len(all_schemas)):
            schema = all_schemas[i]
            schema_id = schema["id"]

            schema_name = schema["name"]
            schema_description = schema["description"]

            # if schema['name'] != "OrderManagementTableau":
            #     continue

            schema_views = schemas.get_schema_views(schema['name'], True)

            for j in range(0, len(schema_views)):
                view = schema_views[j]
                chroma_id = f"schema_{schema_id}_view_{view['name']}"
                prev_embedding = views_collection.get(ids=[chroma_id])

                if len(prev_embedding['ids']) > 0:
                    logger.system_message(f'Found previous embedding for view in schema: {schema_name} id: {chroma_id}')
                    continue

                logger.trace(f"Processing schema: {i}/{len(all_schemas)}, view: {j}/{len(schema_views)}")

                schema_view_str = get_trimmed_view_str(view, 7000)

                view_keywords = generate_view_summary(view)

                view_doc = f"schemaName: {schema_name}\n" \
                           f"schemaDescription: {schema_description}\n" \
                           f"FurtherKeywords: {view_keywords}\n" \
                           f"viewInfo: {schema_view_str}"

                network.retry(lambda: views_collection.add(
                    documents=[view_doc],
                    metadatas=[{"type": "business_view", "schema_name": schema_name, "schema_id": schema_id,
                                "schema_description": f"{schema_description}", "view_name": f"{view['name']}",
                                "view_keywords": f"{view_keywords}", "view_columns": f"{str(view['columns'])}"}],
                    ids=[chroma_id]
                ))

                time.sleep(1)  # Wait for 2 seconds before attempting the next view, to avoid rate limiter

    logger.system_message("Query history for relevant results, with query: " + query)

    return views_collection.query(
        query_texts=[query],
        n_results=n
    )


def get_top_relevant_view(n, query):
    results = get_top_relevant_schemas_results(n, query)
    metadatas = results['metadatas'][0]

    result = [
        {
            "id": schema['schema_id'],
            "schema_name": schema['schema_name'],
            "view_name": schema['view_name'],
            "view_columns": schema['view_columns']
        }
        for schema in metadatas]

    logger.system_message("Got relevant schemas:")
    logger.operator_response(result)

    return result
