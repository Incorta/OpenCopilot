import sdk.utils.logger as logger


def get_gpt_human_input(messages):
    logger.system_message("Ask ChatGPT 4, using the following text:")
    logger.print_gpt_messages(messages)

    logger.system_message("Now Copy his response and paste it here (Write END on the last line to stop)):")

    res = ""
    while True:
        line = input()
        if line.strip() == "END":  # you can use any specific terminator string
            break
        res += "\n" + line

    return res
