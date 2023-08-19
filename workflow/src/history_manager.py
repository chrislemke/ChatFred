"""This module handles the history searching and matching when you compose a new message with 'cf'"""

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

if os.getenv("alternative_key"):
    __model = os.getenv("alternative_model")
else:
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

    if os.getenv("uuid_") is None or os.getenv("user_prompt") != prompt:
        # Return the result without history once first in case
        # the history or the prompt is too long
        # for the full history to generate
        # within a reasonable amount of time

        # Lag is mostly caused by process.extract()

        # Utilized an Alfred feature that the variables'
        # field will be passed back through to reruns of
        # script from the same session
        # Significantly increases speed for long prompts & long history
        uuid_ = str(uuid.uuid1())

        pre_history_dict = {
            "variables": {"user_prompt": prompt, "uuid_": uuid_},
            "rerun": 0.1,
            "items": [
                {
                    "type": "default",
                    "title": prompt,
                    "subtitle": f"Talk to {__model} 💬".strip(),
                    "arg": [uuid_, prompt],
                    "autocomplete": prompt,
                    "icon": {"path": "./icon.png"},
                }
            ],
        }

        stdout_write(json.dumps(pre_history_dict))

        return

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
        history = [tuple_[0] for tuple_ in process.extract(prompt, history, limit=20)]

    history.insert(
        0,
        (
            os.getenv("uuid_"),
            prompt if prompt.strip() else "...",
            f"Talk to {__model} 💬",
            "0",
        ),
    )

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

    stdout_write(json.dumps(response_dict))

    return


provide_history()
