import csv
import os.path
from datetime import datetime
from service.configs.service_env import consumption_report_path, consumption_report_filename
from opencopilot.configs import constants
from tabulate import tabulate


class ConsumptionTracker:
    max_file_size = 1 * 1024 * 1024
    lines_to_delete = 20

    def __init__(self, chat_id):
        self.session_id = chat_id
        self.consumption_tracking = {
            constants.planner: [],
            constants.executor: []
        }
        self.total_consumption = 0.0

    @staticmethod
    def create_consumption_unit(model_name="", total_tokens=0, prompt_tokens=0, completion_tokens=0, successful_requests=0, total_cost=0.0):
        return {
            "model_name": model_name,
            "operator": "",
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "successful_requests": successful_requests,
            "total_cost": total_cost
        }

    def add_consumption(self, consumption, handler, operator):
        if consumption is None:  # No call to GPT was made (Execution was predefined or retrieved from cache)
            consumption = self.create_consumption_unit()
        consumption["operator"] = operator
        self.consumption_tracking[handler].append(consumption)

    def print_consumption_report(self):
        planner_total_cost = sum(
            step["total_cost"] for step in self.consumption_tracking[constants.planner]
        )
        executor_total_cost = sum(
            step["total_cost"] for step in self.consumption_tracking[constants.executor]
        )
        self.total_consumption = planner_total_cost + executor_total_cost

        print("\n\nConsumption Report")
        print("------------------")
        print(f"Total Consumption: ${self.total_consumption:.6f}")

        print("\nPlanning Consumption:")
        planning_table = self.create_consumption_table(self.consumption_tracking[constants.planner])
        print(tabulate(planning_table, headers="keys", tablefmt="grid"))

        print("\nExecution Consumption:")
        execution_table = self.create_consumption_table(self.consumption_tracking[constants.executor])
        print(tabulate(execution_table, headers="keys", tablefmt="grid"))

        if consumption_report_path != "":
            self.write_consumption_report_to_csv(consumption_report_path + consumption_report_filename)

    @staticmethod
    def create_consumption_table(steps):
        table = []
        for i, step in enumerate(steps, start=1):
            table.append({
                "Operator": f"{step['operator']}",
                "Cost": f"${step['total_cost']:.6f}"
            })

        return table

    def write_consumption_report_to_csv(self, file_path):
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
                "Total Tokens",
                "Prompt Tokens",
                "Completion Tokens",
                "Total Cost ($)"
            ]

            writer = csv.DictWriter(report_file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            for step in self.consumption_tracking[constants.planner]:
                writer.writerow({
                    "Timestamp": timestamp,
                    "Category": "Planning Consumption",
                    "Model": step['model_name'],
                    "Operator": step['operator'],
                    "Total Tokens": step['total_tokens'],
                    "Prompt Tokens": step['prompt_tokens'],
                    "Completion Tokens": step['completion_tokens'],
                    "Total Cost ($)": f"{step['total_cost']:.6f}"
                })

            for i, task in enumerate(self.consumption_tracking[constants.executor], start=1):
                writer.writerow({
                    "Timestamp": timestamp,
                    "Category": f"Task {i}",
                    "Model": task['model_name'],
                    "Operator": task["operator"],
                    "Total Tokens": task['total_tokens'],
                    "Prompt Tokens": task['prompt_tokens'],
                    "Completion Tokens": task['completion_tokens'],
                    "Total Cost ($)": f"{task['total_cost']:.6f}"
                })

            # Write the last row with the total cost from all previous rows
            writer.writerow({
                "Session ID": self.session_id,
                "Timestamp": timestamp,
                "Category": "Total Execution Cost",
                "Model": "",  # Leave empty
                "Operator": "",  # Leave empty
                "Total Tokens": "",  # Leave empty
                "Prompt Tokens": "",  # Leave empty
                "Completion Tokens": "",  # Leave empty
                "Total Cost ($)": f"{self.total_consumption:.6f}"
            })

        print(f"\n--> Get the full report at '{os.path.abspath(file_path)}'\n\n")
