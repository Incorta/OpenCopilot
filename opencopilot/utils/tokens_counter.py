import tiktoken


def count_prompt_tokens(prompt):
    encoding = tiktoken.encoding_for_model("gpt-4o")
    current_tokens = len(encoding.encode(str(prompt)))
    return current_tokens
