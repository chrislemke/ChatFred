"""This module contains the chatGPT API."""

import os
import sys
from typing import Optional, Tuple

from custom_chat_prompts import clear_log_prompts
from error_handling import env_value_error_if_needed, exception_response

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import openai

openai.api_key = os.getenv("api_key")

__history_length = int(os.getenv("history_length") or 2)
__temperature = float(os.getenv("temperature") or 0.0)
__max_tokens = int(os.getenv("max_tokens")) if os.getenv("max_tokens") else None  # type: ignore
__top_p = int(os.getenv("top_p") or 1)
__frequency_penalty = float(os.getenv("frequency_penalty") or 0.0)
__presence_penalty = float(os.getenv("presence_penalty") or 0.0)
__workflow_data_path = os.getenv("alfred_workflow_data") or os.path.expanduser("~")
__log_file_path = f"{__workflow_data_path}/ChatFred_ChatGPT.log"
__jailbreak_prompt = os.getenv("jailbreak_prompt")


def get_query() -> str:
    """Join the arguments into a query string."""
    return " ".join(sys.argv[1:])


def stdout_write(output_string: str) -> None:
    """Writes the response to stdout."""
    output_string = "..." if output_string == "" else output_string
    sys.stdout.write(output_string)


def exit_on_error() -> None:
    """Checks the environment variables for invalid values."""
    error = env_value_error_if_needed(
        __temperature,
        "gpt-3.5-turbo",
        __max_tokens,
        __frequency_penalty,
        __presence_penalty,
    )
    if error:
        stdout_write(error)
        sys.exit(0)


def read_from_log() -> list[str]:
    """Reads the log file and returns the last __history_length lines."""
    history: list[str] = []
    if os.path.isfile(__log_file_path) is False:
        return history

    with open(__log_file_path, "r", encoding="utf-8") as log_file:
        logs = log_file.readlines()

    for line in logs:
        line = line.replace("\n", "")
        history.append(line)

    return history[: __history_length * 2]


def write_to_log(
    user_input: str, assistant_output: str, jailbreak_prompt: Optional[str] = None
) -> None:
    """Writes the user input and the assistant output to the log file."""

    if not os.path.exists(__workflow_data_path):
        os.makedirs(__workflow_data_path)

    with open(__log_file_path, "a+", encoding="utf-8") as log:
        if jailbreak_prompt:
            log.write(f"user: {jailbreak_prompt}\n")
        log.write(f"user: {user_input[3:] if user_input[:2] == '-j' else user_input}\n")
        log.write(f"assistant: {assistant_output}\n")


def remove_log_file() -> None:
    """Removes the log file."""
    if os.path.isfile(__log_file_path):
        os.remove(__log_file_path)


def handle_custom_prompts(prompt: str):
    """Handles custom prompts.

    Currently only the clear log prompts.
    """
    if prompt in clear_log_prompts:
        remove_log_file()
        stdout_write("All my memories of you have been erased 😢")
        sys.exit(0)


def create_message(prompt: str):
    """Creates the messages for the OpenAI API request."""

    messages = [{"role": "system", "content": "You are a helpful assistant"}]

    for text in read_from_log():
        if text == (f"user: {__jailbreak_prompt}"):
            continue
        if text.startswith("user: "):
            messages.append({"role": "user", "content": text.replace("user: ", "")})
        elif text.startswith("assistant: "):
            messages.append(
                {"role": "assistant", "content": text.replace("assistant: ", "")}
            )
    if __jailbreak_prompt and prompt[:2] == "-j":
        messages.append(
            {"role": "user", "content": __jailbreak_prompt.replace("user: ", "")}
        )
        prompt = prompt[3:]

    messages.append({"role": "user", "content": prompt})
    return messages


def make_chat_request(
    prompt: str,
    temperature: float,
    max_tokens: Optional[int],
    top_p: int,
    frequency_penalty: float,
    presence_penalty: float,
) -> Tuple[str, str]:
    """Makes a request to the OpenAI API and returns the prompt and the
    response."""

    handle_custom_prompts(prompt)
    messages = create_message(prompt)

    try:
        response = (
            openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
            )
            .choices[0]
            .message["content"]
        )

    except Exception as exception:  # pylint: disable=broad-except
        response = exception_response(exception)

    return prompt, response


exit_on_error()
__prompt, __response = make_chat_request(
    get_query(),
    __temperature,
    __max_tokens,
    __top_p,
    __frequency_penalty,
    __presence_penalty,
)
stdout_write(__response)
write_to_log(__prompt, __response, __jailbreak_prompt if __prompt[:2] == "-j" else None)
