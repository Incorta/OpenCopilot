import os
from jinja2 import Environment, FileSystemLoader


def load_template(path, data):
    # Get the directory containing the code file
    dir_path = os.path.dirname(os.path.abspath(__file__))

    # Set up the jinja2 environment to load templates from the current directory
    env = Environment(loader=FileSystemLoader(os.path.join(dir_path, '..')))

    # Load the template from the file
    template = env.get_template(path)

    # Render the template with the data and output the result
    return template.render(data)
