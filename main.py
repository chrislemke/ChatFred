import os
import re
import subprocess
import sys
from typing import List

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


x = __prompt_from_request(sys.argv[1:])

print(x, file=sys.stderr)

response = (
    openai.Completion.create(
        model=os.getenv("model"),
        prompt=x,
        temperature=0,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\n"],
    )
    .choices[0]
    .text
)


print(response, file=sys.stderr)
subprocess.run("pbcopy", text=True, input=response)
