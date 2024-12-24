import re
import json
import opencopilot.utils.logger as logger

def extract_json_block(text):
    string_pattern = r'(".*?")'

    # Function to replace unescaped newline and carriage return characters within strings
    def escape_unescaped_newlines(match):
        string = match.group(0)
        # Escape unescaped newlines and carriage returns
        string = string.replace('\n', '\\n').replace('\r', '\\r')
        return string

    def is_schema(parsed_block):
        return 'type' in parsed_block and 'property' in parsed_block

    # Apply the function to all string literals in the text
    text = re.sub(string_pattern, escape_unescaped_newlines, text, flags=re.DOTALL)
    # Find the last closing curly brace `}`
    last_brace_index = text.rfind('}')
    if last_brace_index == -1:
        raise Exception("No closing curly brace found in the text.")

    # Escape unescaped newlines and carriage returns in the entire text first (before extracting JSON blocks)
    text = re.sub(r'(".*?")', escape_unescaped_newlines, text)

    json_blocks = []
    opening_brace_count = 0
    start_index = None

    for i in range(len(text)):
        if text[i] == '{':
            if opening_brace_count == 0:
                start_index = i  # mark the start of the JSON block
            opening_brace_count += 1
        elif text[i] == '}':
            opening_brace_count -= 1
            if opening_brace_count == 0:
                json_block = text[start_index:i+1]
                try:
                    # Try to parse the JSON block to ensure it's valid JSON
                    parsed_block = json.loads(json_block)
                    # ignore schema jsons
                    if not is_schema(parsed_block):
                        json_blocks.append(json_block)

                except json.JSONDecodeError as e:
                    logger.error("Error parsing JSON block:" + json_block)
                    logger.error("Exception:"+ str(e))
                    pass  # Skip invalid JSON blocks

    if len(json_blocks) == 0:
        logger.error("Error Extracting JSON:")
        logger.error(text)
        raise Exception("No valid JSON blocks found.")
    elif len(json_blocks) > 1:
        logger.error("Error Extracting JSON:")
        logger.error(text)
        raise Exception("More than one valid JSON block returned.")

    # Only one valid JSON block is expected at this point
    json_block = json_blocks[0]

    # Try to parse the extracted JSON block
    try:
        json_block_dict = json.loads(json_block)
    except json.JSONDecodeError as e:
        logger.error("Error parsing JSON:")
        logger.error(json_block)
        logger.error("Exception:" + str(e))
        raise Exception("Error parsing JSON.")

    # Return the extracted JSON block as a pretty-printed string
    return json.dumps(json_block_dict, indent=4)
