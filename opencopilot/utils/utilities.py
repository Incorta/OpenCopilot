import re
import json
import opencopilot.utils.logger as logger

def escape_unescaped_newlines_in_text(text):
    """Escape unescaped newline and carriage return characters in string literals within the text."""
    string_pattern = r'(".*?")'

    def escape_unescaped_newlines(match):
        string = match.group(0)
        return string.replace('\n', '\\n').replace('\r', '\\r')

    return re.sub(string_pattern, escape_unescaped_newlines, text, flags=re.DOTALL)

def extract_json_blocks(text):
    """Extract all JSON blocks from the given text."""
    opening_brace_count = 0
    start_index = None
    json_blocks = []

    for i, char in enumerate(text):
        if char == '{':
            if opening_brace_count == 0:
                start_index = i
            opening_brace_count += 1
        elif char == '}':
            opening_brace_count -= 1
            if opening_brace_count == 0 and start_index is not None:
                json_blocks.append(text[start_index:i + 1])
                start_index = None

    return json_blocks

def validate_and_filter_json_blocks(json_blocks):
    """Validate JSON blocks and filter out schemas."""
    valid_json_blocks = []

    for block in json_blocks:
        try:
            parsed_block = json.loads(block)
            if not is_schema(parsed_block):  # Ignore schema JSONs
                valid_json_blocks.append(parsed_block)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON block: {block}")

    return valid_json_blocks

def is_schema(parsed_block):
    """Determine whether a JSON block is a schema."""
    return 'type' in parsed_block and 'property' in parsed_block

def handle_extracted_blocks(valid_json_blocks):
    """Handle the extracted valid JSON blocks and raise errors for invalid cases."""
    if len(valid_json_blocks) == 0:
        logger.error("No valid JSON blocks found.")
        raise Exception("No valid JSON blocks found.")
    elif len(valid_json_blocks) > 1:
        logger.error("More than one valid JSON block found.")
        raise Exception("More than one valid JSON block found.")

    return valid_json_blocks[0]

def extract_json_block(text):
    """Main function to extract a valid JSON block from text."""
    # Step 1: Escape unescaped newlines and carriage returns
    cleaned_text = escape_unescaped_newlines_in_text(text)

    # Step 2: Extract JSON blocks
    json_blocks = extract_json_blocks(cleaned_text)

    # Step 3: Validate and filter JSON blocks
    valid_json_blocks = validate_and_filter_json_blocks(json_blocks)

    # Step 4: Handle the extracted blocks and return the result
    final_json_block = handle_extracted_blocks(valid_json_blocks)

    # Step 5: Return the pretty-printed JSON block
    return json.dumps(final_json_block, indent=4)
