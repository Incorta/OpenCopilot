import csv
import json
import os
from datetime import datetime
from tabulate import tabulate
from opencopilot.utils import logger
from opencopilot.configs import constants
from opencopilot.utils.langchain.llm_GPT import run
from service.configs.service_env import evaluation_report_path, evaluation_report_filename


class LlmEvaluator:
    max_file_size = 1 * 1024 * 1024
    lines_to_delete = 20

    def __init__(self, chat_id):
        self.session_id = chat_id
        self.llm_ratings = {
            constants.planner: [],
            constants.executor: []
        }
        self.overall_rating = 0.0

    @staticmethod
    def create_evaluation_unit(model_name="", rating=0.0, comments=""):
        return {
            "model_name": model_name,
            "operator": "",
            "rating": rating,
            "comments": comments
        }

    def add_llm_evaluation(self, evaluation, handler, operator):
        if evaluation is None:  # No call to GPT was made (Execution was predefined or retrieved from cache)
            evaluation = self.create_evaluation_unit()
        evaluation["operator"] = operator
        self.llm_ratings[handler].append(evaluation)

    def print_evaluation_report(self):
        planner_rating = sum(
            step["rating"] for step in self.llm_ratings[constants.planner]
        )
        executor_rating = sum(
            step["rating"] for step in self.llm_ratings[constants.executor]
        )
        print("\n\nEvaluation Report")
        print("------------------")
        try:
            self.overall_rating = (planner_rating + executor_rating) / (len(self.llm_ratings[constants.planner]) + len(self.llm_ratings[constants.executor]))
            print(f"Overall Rating: {self.overall_rating:.1f}/10")

            print("\nPlanning Evaluation:")
            planning_table = self.create_evaluation_table(self.llm_ratings[constants.planner])
            print(tabulate(planning_table, headers="keys", tablefmt="grid"))

            print("\nExecution Evaluation:")
            execution_table = self.create_evaluation_table(self.llm_ratings[constants.executor])
            print(tabulate(execution_table, headers="keys", tablefmt="grid"))

            if evaluation_report_path != "":
                self.write_evaluation_report_to_csv(evaluation_report_path + evaluation_report_filename)

        except ZeroDivisionError:
            print("No new evaluations were made, LLM responses were retrieved from cache!")

    @staticmethod
    def create_evaluation_table(steps):
        table = []
        for i, step in enumerate(steps, start=1):
            table.append({
                "Operator": f"{step['operator']}",
                "Rating": f"{step['rating']:.1f}/10"
            })

        return table

    def write_evaluation_report_to_csv(self, file_path):
        timestamp = datetime.now()
        file_exists = os.path.isfile(file_path)

        if file_exists:
            # Get the current file size
            current_file_size = os.path.getsize(file_path)

            # Check if the file size exceeds 1 MB
            if current_file_size > self.max_file_size:
                # Read the file content and get rid of the first lines_to_delete lines
                with open(file_path, 'r') as file:
                    lines = file.readlines()[self.lines_to_delete:]

                # Write the modified content back to the file
                with open(file_path, 'w') as file:
                    file.writelines(lines)

                print(f"{self.lines_to_delete} lines deleted from the beginning due to size limit.")

        with open(file_path, 'a+', newline='') as report_file:
            fieldnames = [
                "Session ID",
                "Timestamp",
                "Category",
                "Model",
                "Operator",
                "Rating (/10)",
                "Comments"
            ]

            writer = csv.DictWriter(report_file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            for step in self.llm_ratings[constants.planner]:
                writer.writerow({
                    "Timestamp": timestamp,
                    "Category": "Planning Evaluation",
                    "Model": step['model_name'],
                    "Operator": step["operator"],
                    "Rating (/10)": step['rating'],
                    "Comments": step['comments']
                })

            for i, task in enumerate(self.llm_ratings[constants.executor], start=1):
                writer.writerow({
                    "Timestamp": timestamp,
                    "Category": f"Task {i}",
                    "Model": task['model_name'],
                    "Operator": task["operator"],
                    "Rating (/10)": task['rating'],
                    "Comments": task['comments']
                })

            # Write the last row with the overall rating from all previous rows
            writer.writerow({
                "Session ID": self.session_id,
                "Timestamp": timestamp,
                "Category": "Overall Evaluation Rating",
                "Model": "",  # Leave empty
                "Operator": "",  # Leave empty
                "Rating (/10)": f"{self.overall_rating:.1f}",
                "Comments": ""  # Leave empty
            })

        print(f"\n--> Get the full report at '{os.path.abspath(file_path)}'\n\n")


def evaluate_llm_reply(langchain_messages, llm_reply):
    evaluation_prompt = [
        {
            "role": "system",
            "content": f"""You are an LLM evaluation system, I'll give you a prompt sent to an LLM model and the generated response, rate the accuracy, appropriateness and relevance of the response generated by the LLM. Your evaluation should be in JSON format containing 'Rating' and 'Comments' as keys. Rate the performance on a scale of 1-10 and provide comments in 20 words maximum.  Consider factors such as the accuracy of the information, the clarity of the language used, the structure of the response, and how well the response aligns with the initial query or prompt.
    Prompt: {langchain_messages}
    
    LLM response: {llm_reply}
    
JSON:  
                       
    """,
        }
    ]

    try:
        from service.configs.llm_copilot_predefined_model import predefined_model as model
        evaluation, consumption_tracking, model_name = run(evaluation_prompt, model, priority_list_mode=False)
        evaluation = json.loads(evaluation)
        evaluation_unit = LlmEvaluator.create_evaluation_unit(model_name, float(evaluation["Rating"]), evaluation["Comments"])
        return evaluation_unit, consumption_tracking
    except Exception as e:
        logger.error("Error occurred while evaluating llm: " + str(e))
