# OpenCopilot
<img src="/resources/open-copilot-demo.gif" width="896" height="504" />

OpenCopilot is an AI-driven Copilot Agent developed by Incorta. It is designed to allow software companies to create a copilot for their software that can carry out complex tasks 
within the context of the capabilities of the software.

Check [Meet OpenCopilot, Incorta’s Chat Agent](https://medium.com/engineering-incorta/meet-opencopilot-incortas-chatgpt-agent-e110a07b188) and [Comparing OpenCopilot to LangChain’s Plan and Execute Agent](https://medium.com/engineering-incorta/comparing-opencopilot-to-langchains-plan-and-execute-agent-479cf8de88db) for more information on how it works and the motivation behind it.

## Getting Started

The best way to start using OpenCopilot is to run the main example. The main example is a simple copilot for Postgres DB server. Follow these steps to run the example:

### Step 1 : Install Docker:
Make sure you have `Docker` and `Docker-Compose` installed on your machine.

### Step 2 : OpenAI Key:
Note: You can use any llm model from the following AI Providers [Azure, OPENAI], See template json files

- Set the models you want to use by adding the configurations of each model in the llm_copilot_configurations.json file.
- Supported copilot models names ["openai_gpt-3.5-turbo", "openai_gpt-4", "azure-openai_gpt-3.5-turbo" , "azure-openai_gpt-4"]
- Supported embedding models names ["openai_text-embedding-ada-002", "azure-openai_text-embedding-ada-002"]

### Step 3 : Run the container

Navigate to `docker` folder then run the following command to create docker image:
	 `docker-compose up`

### Step 4 : Chat with the OpenCopilot

Once the application is running, you can access it in your web browser at `http://localhost:3000/`. You can try it out by asking the question "What is the total sales?", you should get an answer like the video at the top of the page. 

## How to use

### Adding new operators

The first step in customizing the copilot for your software is usually to create a couple of operators for your software. You can check the folder `service/operators/postgres` for sample operators. Each operators group should be in its own folder. Currently, we support one operators group only. You should define the name of the operators group in the system variable `OPERATORS_GROUPS`. you should also define your OpenAI 3.5 key at least in the system variable OPENAI_GPT35_API_KEY.

Each operator contains one or more command definition. A command is the simplest atomic step that the Copilot understands and executes. Each operator should be defined in a variable named `op_functions`. Check the file `service/operators/postgres/operators_handler.py` for more info.

### Calling OpenCopilot

Check `service/controller` for more information.

For accurate planning and SQL generation, we recommend using GPT-4.

### Install sdk

Run the following command to install OpenCopilot python library:

`pip install opencopilot`

## Contact

To contact OpenCopilot developers with questions and suggestions, please use [GitHub Issues](https://github.com/Incorta/OpenCopilot/issues)
