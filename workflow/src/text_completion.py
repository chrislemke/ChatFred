"""This module contains the InstructGPT API."""

import json
import os
import sys

from error_handling import (
    env_value_error_if_needed,
    exception_response,
    log_error_if_needed,
)

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import openai

openai.api_key = os.getenv("api_key")
__model = os.getenv("model") or "text-davinci-003"
__temperature = float(os.getenv("temperature") or 0.0)
__max_tokens = int(os.getenv("max_tokens") or 50)
__top_p = int(os.getenv("top_p") or 1)
__frequency_penalty = float(os.getenv("frequency_penalty") or 0.0)
__presence_penalty = float(os.getenv("presence_penalty") or 0.0)
__workflow_data_path = os.getenv("alfred_workflow_data") or os.path.expanduser("~")
__workflow_version = os.getenv("alfred_workflow_version") or "unknown"
__debug = int(os.getenv("alfred_debug") or 0)


def get_query() -> str:
    """Join the arguments into a query string."""
    return " ".join(sys.argv[1:])


def prompt_from_query(query: str) -> str:
    """Creates a suitable prompt for the OpenAI API."""
    return f"Q: {query}\nA:"


def stdout_write(output_string: str) -> None:
    """Writes the response to stdout."""
    output_string = "..." if output_string == "" else output_string
    response_dict = {
        "variables": {
            "request": f"{get_query()}",
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
    sys.stdout.write(json.dumps(response_dict))


def exit_on_error() -> None:
    """Checks the environment variables for invalid values."""
    error = env_value_error_if_needed(
        __temperature, __model, __max_tokens, __frequency_penalty, __presence_penalty
    )
    if error:
        stdout_write(error)
        sys.exit(0)


def make_request(
    model: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    top_p: int,
    frequency_penalty: float,
    presence_penalty: float,
) -> str:
    """Makes the request to the OpenAI API."""

    try:
        return (
            openai.Completion.create(
                model=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=["\n", "<|endoftext|>"],
            )
            .choices[0]
            .text
        )
    except Exception as exception:  # pylint: disable=broad-except
        log_error_if_needed(
            model=model,
            error_message=exception._message,  # type: ignore  # pylint: disable=protected-access
            user_prompt=prompt.replace("Q: ", "").split("\n")[0],
            parameters={
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty,
            },
            workflow_data_path=__workflow_data_path,
            workflow_version=__workflow_version,
            debug=__debug,
        )
        return exception_response(exception)


exit_on_error()
response = make_request(
    __model,
    prompt_from_query(get_query()),
    __temperature,
    __max_tokens,
    __top_p,
    __frequency_penalty,
    __presence_penalty,
)
stdout_write(response)
