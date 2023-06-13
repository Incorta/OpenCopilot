from unittest.mock import MagicMock

import pytest

from operators.incorta.api_common import schemas
from utils.exceptions import UnknownCommandError


def test_handle_command_list_schemas():
    schemas.get_schemas_names_and_ids = MagicMock(return_value="schema_list")
    command = {"command_name": "ListSchemas"}
    result = metadata.handle_command(command)
    assert result == "schema_list"
    schemas.get_schmemas_names_and_ids.assert_called_once()


def test_handle_command_list_relevant_schemas():
    schemas.get_relevant_schemas = MagicMock(return_value="relevant_schema_list")
    command = {"command_name": "ListRelevantSchemas"}
    result = metadata.handle_command(command)
    assert result == "relevant_schema_list"
    schemas.get_relevant_schemas.assert_called_once()


def test_handle_command_list_schema_tables():
    schemas.get_schema_tables_and_ids = MagicMock(return_value="schema_tables_list")
    command = {
        "command_name": "ListSchemaTables",
        "args": {"schema_name": "test_schema"}
    }
    result = metadata.handle_command(command)
    assert result == "schema_tables_list"
    schemas.get_schema_tables_and_ids.assert_called_once_with("test_schema")


def test_handle_command_unknown_command():
    command = {"command_name": "UnknownCommand"}
    with pytest.raises(UnknownCommandError) as excinfo:
        metadata.handle_command(command)
    assert str(excinfo.value) == "Unknown command: {command['CommandName']}"
