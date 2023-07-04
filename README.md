# OpenCopilot

OpenCopilot is an AI-driven Copilot Agent developed by Incorta. It is designed to allow software companies to create a copilot for their software that can carry out complex tasks 
within the context of the capabilities of the software. 


## Install

Run the following command to install OpenCopilot python library:

`pip install open-copilot`


## Getting Started

The best way to start using OpenCopilot is to run the main example. The main example is a simple copilot for Postgres DB server. Follow these steps to run the example:

> Before you begin, make sure you have Docker and Docker Compose installed on your machine.

1. Open a terminal or command prompt window and navigate to `examples/postgres/env.py`.
2. Edit the file `env.py` and add your OpenAI Key. You can should add your key to "openai_text_ada_api_key" and either "openai_gpt35_api_key" or "openai_gpt4_api_key". 
3. Run the following command to start the application:
	 `docker-compose up`

Once the application is running, you can access it in your web browser at `http://localhost:3000/`. You can try it out by asking the question "What was the sales last year?". 

For accurate planning and SQL generation, we recommend using GPT-4.

## How to use

### Adding new operators

The first step in customizing the copilot for your software is usually to create a couple of operators for your software. You can check the folder `examples/postgres/operators` for sample operators. Each operators group should be in its own folder. Currently, we support one operators group only. You should define the name of the operators group in the configuration `operators_group` in `env.py` so that OpenCopilot discovers it.

Each operator contains one or more command definition. A command is the simplest atomic step that the Copilot understands and executes. Each operator should be defined in a variable named `op_functions`. Check the file `examples/postgres/operators/postgres/operators_handler.py` for more info.

### Calling OpenCopilot

OpenCopilot exposes one function only named `receive_and_route_user_request.async_run_planning_loop`. This function expects an object that contains the user's query. It can optionally contain a predefined plan. A predefined plan is useful if the use case is simple and a pre-planning process is not required.


## Contact

To contact OpenCopilot developers with questions and suggestions, please use [GitHub Issues](https://github.com/Incorta/OpenCopilot/issues)
