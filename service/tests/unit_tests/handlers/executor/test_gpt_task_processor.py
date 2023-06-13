import unittest
from unittest.mock import patch

from handlers.executor.gpt_task_processor import get_command_prompt_from_task
from utils.exceptions import UnknownCommandError


class TestGetCommandPromptFromTask(unittest.TestCase):

    @patch("handlers.executor.gpt_task_processor.metadata.get_commands_help")
    def test_returns_prompt_for_meta_op_task(self, mock_get_commands_help):
        # Arrange
        tasks = [
            {"id": 1, "operator": "MetaOp", "name": "Task 1", "description": "Description 1", "status": "TODO"},
            {"id": 2, "operator": "UiOp", "name": "Task 2", "description": "Description 2", "status": "TODO"}
        ]
        task_index = 0
        mock_get_commands_help.return_value = {
            "overview": "Some operator help string",
            "commands": [
                {"command_name": "add_table", "args": "table_name, schema_name",
                 "command_description": "Add a table to a schema"},
                {"command_name": "add_join", "args": "table_name_1, table_name_2",
                 "command_description": "Add a join between two tables"}
            ]
        }

        # Act
        result = get_command_prompt_from_task(tasks, task_index)

        # Assert
        self.assertIn("generate the command for Task_id: 1", result)
        self.assertIn("add_table", result)
        self.assertIn("add_join", result)

    @patch("handlers.executor.gpt_task_processor.ui.get_commands_help")
    def test_returns_prompt_for_ui_op_task(self, mock_get_commands_help):
        # Arrange
        tasks = [
            {"id": 1, "operator": "MetaOp", "name": "Task 1", "description": "Description 1", "status": "DONE"},
            {"id": 2, "operator": "UiOp", "name": "Task 2", "description": "Description 2", "status": "TODO"}
        ]
        task_index = 1
        mock_get_commands_help.return_value = {
            "overview": "Some operator help string",
            "commands": [
                {"command_name": "click_button", "args": "button_id", "command_description": "Click a button"},
                {"command_name": "fill_form", "args": "form_id, values", "command_description": "Fill out a form"}
            ]
        }

        # Act
        result = get_command_prompt_from_task(tasks, task_index)

        # Assert
        self.assertIn("generate the command for Task_id: 2", result)
        self.assertIn("click_button", result)
        self.assertIn("fill_form", result)

    def test_raises_error_for_unknown_task_operator(self):
        # Arrange
        tasks = [
            {"id": 1, "operator": "MetaOp", "name": "Task 1", "description": "Description 1", "status": "DONE"},
            {"id": 2, "operator": "UnknownOp", "name": "Task 2", "description": "Description 2", "status": "TODO"}
        ]
        task_index = 1

        # Act/Assert
        with self.assertRaises(UnknownCommandError):
            get_command_prompt_from_task(tasks, task_index)
