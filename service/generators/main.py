import pandas as pd
from configs import env
from generators.analytics_metadata.get_analytics_metadata import construct_analytics_metadata_table
from generators.analytics_metadata.incorta_client import incorta_login
from generators.user_queries.generate_user_queries import generate_user_queries

metadata_filename = 'analytics_metadata_table.csv'


def save_df_to_file(df):
    df.to_csv(metadata_filename)


def read_df_from_file():
    return pd.read_csv(metadata_filename)


if __name__ == '__main__':
    # token, jsessionid, xsrf_token = incorta_login(host=env.incorta_url, user=env.db_jdbc_user, pw=env.db_jdbc_password, tenant=env.db_jdbc_database)
    # metadata_df = construct_analytics_metadata_table(token, jsessionid, xsrf_token)
    # save_df_to_file(metadata_df)
    queries_metadata_df = generate_user_queries(read_df_from_file())
    save_df_to_file(queries_metadata_df)
