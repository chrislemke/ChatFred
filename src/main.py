"""This module contains the OpenAI GPT-3 API call."""

import json
import os
import sys
from typing import List

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import openai

openai.api_key = os.getenv("api_key")


def __query() -> str:
    return " ".join(sys.argv[1:])


def __prompt_from_query(query: str) -> str:
    return f"Q: {query}\nA:"


prompt = __prompt_from_query(__query())

response = (
    openai.Completion.create(
        model=os.getenv("model"),
        prompt=prompt,
        temperature=int(os.getenv("temperature")),  # type: ignore
        max_tokens=int(os.getenv("max_tokens")) + len(prompt),  # type: ignore
        top_p=int(os.getenv("top_p")),  # type: ignore
        frequency_penalty=float(os.getenv("frequency_penalty")),  # type: ignore
        presence_penalty=float(os.getenv("presence_penalty")),  # type: ignore
        stop=["\n"],
    )
    .choices[0]
    .text
)

response = "..." if response == "" else response

response_dict = {
    "variables": {
        "request": f"{__query()}",
    },
    "items": [
        {
            "uid": "null",
            "type": "default",
            "title": response,
            "subtitle": "SHIFT ⇪, CTRL ⌃ or CMD ⌘ for options",
            "arg": response,
            "autocomplete": response,
            "icon": {"path": "./icon.png"},
        }
    ],
}
sys.stdout.write(json.dumps(response_dict))
