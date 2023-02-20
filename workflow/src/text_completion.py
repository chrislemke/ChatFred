"""This module contains the text completion API."""

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import openai

openai.api_key = os.getenv("api_key")
__model = os.getenv("model") or "text-davinci-003"
__temperature = int(os.getenv("temperature") or 0)
__max_tokens = int(os.getenv("max_tokens") or 50)
__top_p = int(os.getenv("top_p") or 1)
__frequency_penalty = float(os.getenv("frequency_penalty") or 0.0)
__presence_penalty = float(os.getenv("presence_penalty") or 0.0)


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


def env_value_checks() -> None:
    """Checks the environment variables for invalid values."""
    if __temperature < 0:
        stdout_write(
            f"🚨 'Temperature' must be ≥ 0. But you have set it to {__temperature}."
        )
        sys.exit(0)

    if __model == "text-davinci-003" and __max_tokens > 4096:
        stdout_write("🚨 'Maximum tokens' must be ≤ 4096 for 'Davinci'.")
        sys.exit(0)

    if (
        __model in ["text-ada-001", "text-babbage-001", "text-curie-001"]
        and __max_tokens > 2048
    ):
        model_name = __model.split("-")[1].capitalize()
        stdout_write(f"🚨 'Maximum tokens' must be ≤ 4096 for '{model_name}'.")
        sys.exit(0)

    if __frequency_penalty <= -2.0 or __frequency_penalty >= 2.0:
        stdout_write("🚨 'Frequency penalty' must be between -2.0 and 2.0.")
        sys.exit(0)

    if __presence_penalty <= -2.0 or __presence_penalty >= 2.0:
        stdout_write("🚨 'Presence penalty' must be between -2.0 and 2.0.")
        sys.exit(0)


def make_request(
    model: str,
    prompt: str,
    temperature: int,
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
    except openai.error.AuthenticationError:
        return "🚨 There seems to be something wrong! Please check your API key."


env_value_checks()
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
