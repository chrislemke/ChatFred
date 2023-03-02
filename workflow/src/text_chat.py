"""This module contains the text completion API."""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import openai

openai.api_key = os.getenv("api_key")
__history_length = int(os.getenv("history_length") or 4)


def get_query() -> str:
    """Join the arguments into a query string."""
    return " ".join(sys.argv[1:])


def read_from_log() -> list[str]:
    history: list[str] = []
    if os.path.isfile(f"{os.path.expanduser('~')}/ChatFred_ChatGPT.log") is False:
        return history

    with open(
        f"{os.path.expanduser('~')}/ChatFred_ChatGPT.log", "r", encoding="utf-8"
    ) as log_file:
        logs = log_file.readlines()

    for line in logs:
        line = line.replace("\n", "")
        history.append(line)

    return history[: __history_length * 2]


def write_to_log(user_input: str, assistant_output: str) -> None:
    with open(
        f"{os.path.expanduser('~')}/ChatFred_ChatGPT.log", "a+", encoding="utf-8"
    ) as log:
        log.write(f"user:{user_input}\n")
        log.write(f"assistant:{assistant_output}\n")


def stdout_write(output_string: str) -> None:
    """Writes the response to stdout."""
    output_string = "..." if output_string == "" else output_string
    {
        "variables": {
            "chat_request": f"{get_query()}",
        },
        "items": [
            {
                "uid": "null",
                "type": "default",
                "title": output_string,
                "subtitle": "⇪, ⌃, ⌥ or ⌘ for options",
                "arg": output_string,
                "autocomplete": output_string,
                "icon": {"path": "./icon.png"},
            }
        ],
    }
    sys.stdout.write(output_string)


def make_chat_request(prompt: str) -> str:
    messages = [{"role": "system", "content": "You are a helpful assistant."}]

    for text in read_from_log():
        if text.startswith("user:"):
            messages.append({"role": "user", "content": text.replace("user:", "")})
        elif text.startswith("assistant:"):
            messages.append(
                {"role": "assistant", "content": text.replace("assistant:", "")}
            )

    messages.append({"role": "user", "content": prompt})

    response = (
        openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        .choices[0]
        .message["content"]
    )

    write_to_log(prompt, response)
    return response


__response = make_chat_request(get_query())
stdout_write(__response)
