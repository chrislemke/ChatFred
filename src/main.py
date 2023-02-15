import json
import os
import re
import sys
from typing import List

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import openai

openai.api_key = os.getenv("api_key")


def __prepare_request(args: List[str]) -> str:
    return " ".join(args).replace("|Q|", "?").replace("|E|", "!").replace("|S|", ".")


def __extract_last_punctuation(sentence: str) -> str:
    punctuation_pattern = r"[\.\?!]"
    match = re.search(punctuation_pattern, sentence)
    if match:
        return sentence[match.end() - 1]
    else:
        return ""


def __prompt_from_request(args: List[str]) -> str:
    request = __prepare_request(args)
    punctuation = __extract_last_punctuation(request)
    if punctuation == "?":
        return f"Q: {request}\nA:"
    return f"{request} A:"


query = __prompt_from_request(sys.argv[1:])

response = (
    openai.Completion.create(
        model=os.getenv("model"),
        prompt=query,
        temperature=int(os.getenv("temperature")),
        max_tokens=int(os.getenv("max_tokens")) + len(query),
        top_p=int(os.getenv("top_p")),
        frequency_penalty=float(os.getenv("frequency_penalty")),
        presence_penalty=float(os.getenv("presence_penalty")),
        stop=["\n"],
    )
    .choices[0]
    .text
)

response_dict = {
    "items": [
        {
            "uid": "null",
            "type": "text",
            "title": response,
            "subtitle": "Hit return to copy.",
            "arg": response,
            "autocomplete": response,
            "icon": {"path": "./icon.png"},
        }
    ]
}

sys.stdout.write(json.dumps(response_dict))
