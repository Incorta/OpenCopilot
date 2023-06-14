from configs import env
from generators.analytics_metadata.get_analytics_metadata import construct_analytics_metadata_table
from generators.analytics_metadata.incorta_client import incorta_login

if __name__ == '__main__':
    token, jsessionid, xsrf_token = incorta_login(host=env.incorta_url, user=env.db_jdbc_user, pw=env.db_jdbc_password, tenant=env.db_jdbc_database)
    construct_analytics_metadata_table(token, jsessionid, xsrf_token)
