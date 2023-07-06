# OpenCopilot

OpenCopilot is an AI-driven Copilot Agent developed by Incorta. It is designed to allow software companies to create a copilot for their software that can carry out complex tasks 
within the context of the capabilities of the software. 


## Install

Run the following command to install OpenCopilot python library:

`pip install opencopilot`


## Getting Started

The best way to start using OpenCopilot is to run the main example. The main example is a simple copilot for Postgres DB server. Follow these steps to run the example:

> Before you begin, make sure you have Docker and Docker Compose installed on your machine.

1. Edit the file `start.sh` and add your OpenAI Key to OPENAI_GPT35_API_KEY.
2. Bavigate to `docker` folder then run the following command to create docker image:
	 `docker-compose up`

Once the application is running, you can access it in your web browser at `http://localhost:3000/`. You can try it out by asking the question "What was the sales last year?". 

## How to use

### Adding new operators

The first step in customizing the copilot for your software is usually to create a couple of operators for your software. You can check the folder `service/operators/postgres` for sample operators. Each operators group should be in its own folder. Currently, we support one operators group only. You should define the name of the operators group in the system variable `OPERATORS_GROUPS`. you should also define your OpenAI 3.5 key at least in the system variable OPENAI_GPT35_API_KEY.

Each operator contains one or more command definition. A command is the simplest atomic step that the Copilot understands and executes. Each operator should be defined in a variable named `op_functions`. Check the file `service/operators/postgres/operators_handler.py` for more info.

### Calling OpenCopilot

Check `service/controller` for more information.

For accurate planning and SQL generation, we recommend using GPT-4.


## Contact

To contact OpenCopilot developers with questions and suggestions, please use [GitHub Issues](https://github.com/Incorta/OpenCopilot/issues)
