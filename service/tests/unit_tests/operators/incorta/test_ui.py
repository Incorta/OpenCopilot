import json
import os
import unittest

from handlers.receive_and_route_user_request import execute_task


class TestExecuteUiOperator(unittest.TestCase):

    os.chdir("../../../")

    def test_execute_query_operator(self):
        with open('tests/operators/incorta/test_files/test_uiOp_tasks.txt', 'r') as file:
            tasks = json.loads(file.read())
        task_index = 2

        execute_task(tasks, task_index)
        result = tasks[task_index]["result"]
        self.assertIsNotNone(result)


