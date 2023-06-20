import os.path
import pandas as pd
from configs import env
from generators.analytics_metadata.get_analytics_metadata import construct_analytics_metadata_table
from generators.analytics_metadata.incorta_client import incorta_login
from generators.queries_to_BV.generate_queries_to_business_views_table import generate_queries_to_bv_table
from generators.user_queries.generate_user_queries import generate_user_queries

metadata_filename = os.path.abspath('generators/analytics_metadata_table.csv')
queries_bv_filename = os.path.abspath('generators/queries_to_BV/queries_to_BV_table.csv')


def save_df_to_file(df, filename):
    df.to_csv(filename)


def read_df_from_file(filename):
    return pd.read_csv(filename)


def construct_analytics_metadata_file():
    token, jsessionid, xsrf_token = incorta_login(host=env.incorta_url, user=env.db_jdbc_user, pw=env.db_jdbc_password, tenant=env.db_jdbc_database)
    metadata_df = construct_analytics_metadata_table(token, jsessionid, xsrf_token)
    save_df_to_file(metadata_df, metadata_filename)


def add_user_queries_to_metadata_file():
    queries_metadata_df = generate_user_queries(read_df_from_file(metadata_filename))
    save_df_to_file(queries_metadata_df, metadata_filename)


def generate_business_view_op_table():
    queries_to_bv_df = generate_queries_to_bv_table(read_df_from_file(metadata_filename))
    save_df_to_file(queries_to_bv_df, queries_bv_filename)


if __name__ == '__main__':
    construct_analytics_metadata_file()
    add_user_queries_to_metadata_file()
    generate_business_view_op_table()

