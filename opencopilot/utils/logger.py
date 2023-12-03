import json
import os
import logging
from logging.handlers import RotatingFileHandler
from termcolor import colored

COLOR_BLACK = "black"
COLOR_RED = "red"
COLOR_GREEN = "green"
COLOR_YELLOW = "yellow"
COLOR_BLUE = "blue"
COLOR_MAGENTA = "magenta"
COLOR_CYAN = "cyan"
COLOR_WHITE = "white"
COLOR_LIGHT_GREY = "light_grey"
COLOR_DARK_GREY = "dark_grey"
COLOR_LIGHT_RED = "light_red"
COLOR_LIGHT_GREEN = "light_green"
COLOR_LIGHT_YELLOW = "light_yellow"
COLOR_LIGHT_BLUE = "light_blue"
COLOR_LIGHT_MAGENTA = "light_magenta"
COLOR_LIGHT_CYAN = "light_cyan"

all_colors = [COLOR_BLACK, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_BLUE, COLOR_MAGENTA, COLOR_CYAN, COLOR_WHITE, COLOR_LIGHT_GREY, COLOR_DARK_GREY, COLOR_LIGHT_RED, COLOR_LIGHT_GREEN,
              COLOR_LIGHT_YELLOW, COLOR_LIGHT_BLUE, COLOR_LIGHT_MAGENTA, COLOR_LIGHT_CYAN]

def setup_logger():
    global __internal_logger
    if __internal_logger is not None:
        return __internal_logger
    # Read the COPILOT_LOG_LEVEL environment variable
    log_level_str = os.environ.get("COPILOT_LOG_LEVEL", "ERROR")

    # Convert log level string to integer value
    log_level = getattr(logging, log_level_str.upper(), logging.ERROR)

    # Set up the logging configuration with a rotating file handler
    log_file = 'logs/app.log'
    max_file_size_bytes = 1024 * 1024 * 256  # 256 MB
    backup_count = 3  # Number of backup files to keep

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create the directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a rotating file handler
    rotating_handler = RotatingFileHandler(log_file, maxBytes=max_file_size_bytes, backupCount=backup_count)
    rotating_handler.setFormatter(formatter)

    # Create a logger and add the rotating file handler
    __internal_logger = logging.getLogger(__name__)
    __internal_logger.addHandler(rotating_handler)
    __internal_logger.setLevel(log_level)

    return __internal_logger

__internal_logger = None
setup_logger()

def print_all_colors():
    for color in all_colors:
        print_colored(f"Hello world!: {color}", color)


def info(message):
    print_colored(message, COLOR_LIGHT_GREEN)
    __internal_logger.info(message)


def trace(message):
    print_colored(message, COLOR_YELLOW)
    __internal_logger.trace(message)


def error(message):
    print_colored(message, COLOR_RED)
    __internal_logger.error(message)


def operator_response(message):
    print_colored(message, COLOR_DARK_GREY)
    __internal_logger.debug(message)


def operator_input(message):
    print_colored(message, COLOR_DARK_GREY)
    __internal_logger.debug(message)


def system_message(message):
    print_colored(message, COLOR_BLUE)
    __internal_logger.debug(message)


def predefined_message(message):
    print_colored(message, COLOR_MAGENTA)
    __internal_logger.debug(message)


def print_colored(message, color):
    if __internal_logger.isEnabledFor(logging.INFO):
        print(colored(message, color))


def print_tasks(tasks_json_array):
    for task in tasks_json_array:
        color = COLOR_YELLOW if task["status"] == "TODO" else COLOR_GREEN
        print_colored(json.dumps(task), color)
        __internal_logger.debug(json.dumps(task))
        


def print_gpt_messages(messages):
    for message in messages:
        role = message['role']
        content = message['content']
        operator_response(f"{role}: {content}")

