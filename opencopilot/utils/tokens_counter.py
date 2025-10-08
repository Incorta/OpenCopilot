import tiktoken


def count_prompt_tokens(prompt):
    encoding = tiktoken.encoding_for_model("gpt-oss-120b")
    current_tokens = len(encoding.encode(str(prompt)))
    return current_tokens
