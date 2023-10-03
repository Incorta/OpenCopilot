import csv
import os.path
from datetime import datetime

from service.configs.service_env import consumption_report_path, consumption_report_filename


class ConsumptionTracker:

    def __init__(self, chat_id):
        self.session_id = chat_id
        self.consumption_tracking = {
            "planner_consumption": {},
            "execution": []
        }

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

    def set_planner_consumption(self, planner_consumption, level):
        if planner_consumption is None:  # No call to GPT was made (Plan was predefined or retrieved from cache)
            planner_consumption = self.create_consumption_unit()
        planner_consumption["operator"] = level
        self.consumption_tracking["planner_consumption"] = planner_consumption

    def add_executor_consumption(self, execution_step, operator):
        if execution_step is None:  # No call to GPT was made (Execution was predefined or retrieved from cache)
            execution_step = self.create_consumption_unit()
        execution_step["operator"] = operator
        self.consumption_tracking["execution"].append(execution_step)

    def print_consumption_report(self):
        planner_consumption = self.consumption_tracking["planner_consumption"]
        executor_total_cost = sum(
            step["total_cost"] for step in self.consumption_tracking["execution"]
        )
        total_consumption = planner_consumption["total_cost"] + executor_total_cost

        print("\n\nConsumption Report")
        print("------------------")
        print(f"Total Consumption: ${total_consumption:.6f}")
        print("  Planning Consumption:")
        print(f"    Cost: ${planner_consumption['total_cost']:.6f}")
        print("  Execution Consumption:")
        for i, step in enumerate(self.consumption_tracking["execution"], start=1):
            print(f"    Task {i}:")
            print(f"      Cost: ${step['total_cost']:.6f}")

        if consumption_report_path != "":
            self.write_consumption_report_to_csv(consumption_report_path + consumption_report_filename)

    def write_consumption_report_to_csv(self, file_path):
        timestamp = datetime.now()
        file_exists = os.path.isfile(file_path)

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

            planner_consumption = self.consumption_tracking["planner_consumption"]

            writer.writerow({
                "Timestamp": timestamp,
                "Category": "Planning Consumption",
                "Model": planner_consumption['model_name'],
                "Operator": planner_consumption["operator"],
                "Total Tokens": planner_consumption['total_tokens'],
                "Prompt Tokens": planner_consumption['prompt_tokens'],
                "Completion Tokens": planner_consumption['completion_tokens'],
                "Total Cost ($)": f"{planner_consumption['total_cost']:.6f}"
            })

            # Set the total cost initially to the planning cost
            total_execution_cost = planner_consumption['total_cost']

            for i, task in enumerate(self.consumption_tracking["execution"], start=1):
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
                # Add the cost of this task to the total cost
                total_execution_cost += task['total_cost']

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
                "Total Cost ($)": f"{total_execution_cost:.6f}"
            })

        print(f"\n--> Get the full report at {os.path.abspath(file_path)}\n\n")
