import unittest
import json
from opencopilot.utils.utilities import (
    escape_unescaped_newlines_in_text,
    extract_json_blocks,
    validate_and_filter_json_blocks,
    is_schema,
    handle_extracted_blocks,
    extract_json_block,
)

class TestJsonBlockExtractor(unittest.TestCase):

    def test_escape_unescaped_newlines_in_text(self):
        input_text = '{"key": "value\nanother value\r"}'
        expected_output = '{"key": "value\\nanother value\\r"}'
        self.assertEqual(escape_unescaped_newlines_in_text(input_text), expected_output)

    def test_extract_json_blocks(self):
        input_text = '{"key1": "value1"} some text {"key2": "value2"}'
        expected_blocks = ['{"key1": "value1"}', '{"key2": "value2"}']
        self.assertEqual(extract_json_blocks(input_text), expected_blocks)

    def test_validate_and_filter_json_blocks(self):
        json_blocks = [
            '{"type": "schema", "property": "value"}',  # schema block
            '{"key": "value"}',  # valid block
            '{"invalid_json": '  # invalid block
        ]
        expected_valid_blocks = [{'key': 'value'}]  # Only the valid block remains
        self.assertEqual(validate_and_filter_json_blocks(json_blocks), expected_valid_blocks)

    def test_is_schema(self):
        schema_block = {"type": "schema", "property": "value"}
        non_schema_block = {"key": "value"}
        self.assertTrue(is_schema(schema_block))
        self.assertFalse(is_schema(non_schema_block))

    def test_handle_extracted_blocks(self):
        valid_blocks = [{"key": "value"}]
        self.assertEqual(handle_extracted_blocks(valid_blocks), {"key": "value"})

        no_blocks = []
        with self.assertRaises(Exception) as context:
            handle_extracted_blocks(no_blocks)
        self.assertEqual(str(context.exception), "No valid JSON blocks found.")

        multiple_blocks = [{"key": "value1"}, {"key": "value2"}]
        with self.assertRaises(Exception) as context:
            handle_extracted_blocks(multiple_blocks)
        self.assertEqual(str(context.exception), "More than one valid JSON block found.")

    def test_extract_json_block(self):
        input_text = '{"key": "value"}'
        expected_output = json.dumps({"key": "value"}, indent=4)
        self.assertEqual(extract_json_block(input_text), expected_output)

        # Test with invalid JSON input
        invalid_text = '{"key": "value"'
        with self.assertRaises(Exception) as context:
            extract_json_block(invalid_text)
        self.assertEqual(str(context.exception), "No valid JSON blocks found.")

        # Test with multiple JSON blocks
        multiple_json_text = '{"key1": "value1"} some text {"key2": "value2"}'
        with self.assertRaises(Exception) as context:
            extract_json_block(multiple_json_text)
        self.assertEqual(str(context.exception), "More than one valid JSON block found.")

if __name__ == "__main__":
    unittest.main()
