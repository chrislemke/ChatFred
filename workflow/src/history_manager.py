"""This module contains the chatGPT API."""

import csv
import json
import os
import sys
import uuid
from typing import List, Tuple

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

from thefuzz import process

__workflow_data_path = os.getenv("alfred_workflow_data") or os.path.expanduser("~")
__log_file_path = f"{__workflow_data_path}/ChatFred_ChatGPT.csv"
__history_type = os.getenv("history_type")
__model = os.getenv("chat_gpt_model") or "gpt-3.5-turbo"


def get_query() -> str:
    """Join the arguments into a query string."""
    return " ".join(sys.argv[1:])


def stdout_write(output_string: str) -> None:
    """Writes the response to stdout."""
    sys.stdout.write(output_string)


def provide_history():
    """Provide the history of the user."""
    prompt = get_query()
    history: List[Tuple[str, str, str, str]] = []

    if not os.path.exists(__workflow_data_path):
        os.makedirs(__workflow_data_path)

    if os.path.exists(__log_file_path):
        with open(__log_file_path, "r") as csv_file:
            csv.register_dialect("custom", delimiter=" ", skipinitialspace=True)
            reader = csv.reader(csv_file, dialect="custom")
            for row in reader:
                if row[3] == "0":
                    history.append((row[0], row[1], row[2], row[3]))

    history = list(reversed(history))
    if __history_type == "search" and prompt != "":
        history = [tuple[0] for tuple in process.extract(prompt, history, limit=20)]

    if prompt in ["", " "]:
        history.insert(0, (str(uuid.uuid1()), "...", f"Talk to {__model} 💬", "0"))
    else:
        history.insert(0, (str(uuid.uuid1()), prompt, f"Talk to {__model} 💬", "0"))

    non_hist_text = [prompt, "..."]

    response_dict = {
        "variables": {
            "user_prompt": prompt,
        },
        "items": [
            {
                "type": "default",
                "title": entry[1],
                "subtitle": entry[2].strip(),
                "arg": [entry[0], entry[1]],
                "autocomplete": entry[1],
                "icon": {
                    "path": f"./{'icon.png' if index == 0 and entry[1] in non_hist_text else 'magnifying_glass.png'}"
                },
            }
            for index, entry in enumerate(history)
        ],
    }
    sys.stdout.write(json.dumps(response_dict))


provide_history()
