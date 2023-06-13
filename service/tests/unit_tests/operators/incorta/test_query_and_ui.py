import json
import os
import unittest

from handlers.planner import gpt_planner
from handlers.receive_and_route_user_request import execute_task
from utils import logger


class TestExecuteQueryAndUiOperators(unittest.TestCase):
    os.chdir("../../../")

    def test_execute_query_operator(self):
        with open('tests/operators/incorta/test_files/test_query_ui_op_tasks.txt', 'r') as file:
            tasks = json.loads(file.read())

        while True:
            next_task_index = gpt_planner.get_next_todo_task_index(tasks)
            execute_task(tasks, next_task_index)

            logger.system_message("Current tasks:")
            logger.print_tasks(tasks)

            if next_task_index < 0:
                break

        result = tasks[next_task_index]["result"]
        self.assertIsNotNone(result)
