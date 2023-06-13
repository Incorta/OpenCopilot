import json
import os
import unittest

from handlers.receive_and_route_user_request import execute_task
from operators.incorta.api_helpers.connect_jdbc import run_sql_query_jdbc


class TestExecuteQueryOperator(unittest.TestCase):
    os.chdir("../../../")

    def test_execute_query_operator(self):
        with open('tests/operators/incorta/test_files/test_queryOp_tasks.txt', 'r') as file:
            tasks = json.loads(file.read())
        task_index = 1

        execute_task(tasks, task_index)
        result = tasks[task_index]["result"]

        self.assertIsNotNone(result)

    def test_run_sql_query_jdbc(self):
        sql_query = "SELECT SUM(ANNUALIZED_SALARY) as total_employee_cost, ORGANIZATION_NAME as department FROM WorkforceDeployment.CompensationCostReport GROUP BY ORGANIZATION_NAME;"

        result = run_sql_query_jdbc(sql_query)

        self.assertIsNotNone(result)

    def test_run_sql_query_data_types_jdbc(self):
        sql_query = "SELECT SalesOrderNumber, OrderDate, StateProvinceName, CategoryName, SubcategoryName, ProductName, Style, LineTotal, LineCost, Profit, Margin FROM Online_Store.RevenueDetail WHERE OrderDate BETWEEN '2013-01-01' AND '2013-12-31' LIMIT 10;"

        result = run_sql_query_jdbc(sql_query)

        self.assertIsNotNone(result)

    def test_run_sql_query_data_types_int_jdbc(self):
        sql_query = "SELECT CategoryName AS Category, COUNT(ProductName) AS Items_Sold, SUM(LineTotal) AS Revenue FROM Online_Store.RevenueDetail GROUP BY CategoryName LIMIT 10;"

        result = run_sql_query_jdbc(sql_query)

        self.assertIsNotNone(result)





