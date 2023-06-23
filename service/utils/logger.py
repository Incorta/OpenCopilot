import json
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


def print_all_colors():
    for color in all_colors:
        print(colored(f"Hello world!: {color}", color))


def trace(message):
    print(colored(message, COLOR_YELLOW))


def error(message):
    print(colored(message, COLOR_RED))


def operator_response(message):
    print(colored(message, COLOR_DARK_GREY))


def operator_input(message):
    print(colored(message, COLOR_DARK_GREY))


def system_message(message):
    print(colored(message, COLOR_BLUE))


def predefined_message(message):
    print(colored(message, COLOR_MAGENTA))


def print_colored(message, color):
    print(colored(message, color))


def print_tasks(tasks_json_array):
    for task in tasks_json_array:
        color = COLOR_YELLOW if task["status"] == "TODO" else COLOR_GREEN
        print_colored(json.dumps(task, indent=4), color)


def print_gpt_messages(messages):
    for message in messages:
        role = message['role']
        content = message['content']
        operator_response(f"{role}: {content}")
