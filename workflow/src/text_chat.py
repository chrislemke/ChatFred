"""This module contains the chatGPT API."""

import csv
import os
import sys
import uuid
from typing import List, Optional, Tuple

from aliases_manager import prompt_for_alias
from caching_manager import read_from_cache, write_to_cache
from custom_prompts import clear_log_prompts, error_prompts
from error_handler import (
    env_value_error_if_needed,
    exception_response,
    get_last_error_message,
    log_error_if_needed,
)

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import openai

openai.api_key = os.getenv("api_key")


__history_length = int(os.getenv("history_length") or 4)
__temperature = float(os.getenv("temperature") or 0.0)
__max_tokens = int(os.getenv("max_tokens")) if os.getenv("max_tokens") else None  # type: ignore
__top_p = int(os.getenv("top_p") or 1)
__frequency_penalty = float(os.getenv("frequency_penalty") or 0.0)
__presence_penalty = float(os.getenv("presence_penalty") or 0.0)
__workflow_data_path = os.getenv("alfred_workflow_data") or os.path.expanduser("~")
__log_file_path = f"{__workflow_data_path}/ChatFred_ChatGPT.csv"
__text_transformation_prompt = os.getenv("text_transformation_prompt") or None
__jailbreak_prompt = os.getenv("jailbreak_prompt")
__unlocked = int(os.getenv("unlocked") or 0)


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


def read_from_log() -> List[Tuple[str, str]]:
    if os.path.isfile(__log_file_path) is False:
        return [("", "")]

    with open(__log_file_path, "r") as csv_file:
        csv.register_dialect("custom", delimiter=" ", skipinitialspace=True)
        reader = csv.reader(csv_file, dialect="custom")

        history = []
        for row in reader:
            history.append((row[1], row[2]))

    return history[-__history_length:]


def write_to_log(
    user_input: str, assistant_output: str, jailbreak_prompt: Optional[str] = None
) -> None:
    """Writes the user input and the assistant output to the log file."""

    if not os.path.exists(__workflow_data_path):
        os.makedirs(__workflow_data_path)

    with open(__log_file_path, "a+") as csv_file:
        csv.register_dialect("custom", delimiter=" ", skipinitialspace=True)
        writer = csv.writer(csv_file, dialect="custom")
        if jailbreak_prompt:
            writer.writerow(
                [str(uuid.uuid4()), jailbreak_prompt, "Okay! How can I help?", 1]
            )
        writer.writerow([str(uuid.uuid4()), user_input, assistant_output, 0])


def remove_log_file() -> None:
    """Removes the log file."""
    if os.path.isfile(__log_file_path):
        os.remove(__log_file_path)


def intercept_custom_prompts(prompt: str):
    """Intercepts custom queries."""

    last_request_successful = read_from_cache("last_chat_request_successful")
    if prompt in error_prompts and not last_request_successful:
        stdout_write(
            f"😬 Sorry, the error message was not really helpful. Here is the original message from OpenAI:\n\n➡️ {get_last_error_message()}"
        )
        write_to_cache("last_chat_request_successful", True)
        sys.exit(0)

    if prompt in clear_log_prompts:
        remove_log_file()
        stdout_write("All my memories of you have been erased 😢")
        sys.exit(0)


def create_message(prompt: str):
    """Creates the messages for the OpenAI API request."""
    transformation_pre_prompt = """You are a helpful assistant who interprets every input as raw
    text unless instructed otherwise. Your answers do not include a description unless prompted to do so."""

    if __text_transformation_prompt:
        return [
            {"role": "system", "content": transformation_pre_prompt},
            {
                "role": "user",
                "content": f"{__text_transformation_prompt} Don't add any comments: {prompt}",
            },
        ]

    messages = [{"role": "system", "content": "You are a helpful assistant"}]
    for user_text, assistant_text in read_from_log():
        if user_text == __jailbreak_prompt:
            continue
        messages.append({"role": "user", "content": user_text})
        messages.append({"role": "assistant", "content": assistant_text})

    if __jailbreak_prompt and __unlocked == 1:
        messages.append({"role": "user", "content": __jailbreak_prompt})
        messages.append({"role": "assistant", "content": "Okay! How can I help?"})

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

    intercept_custom_prompts(prompt)
    prompt = prompt_for_alias(prompt)
    messages = create_message(prompt)
    write_to_cache("last_chat_request_successful", True)

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
        write_to_cache("last_chat_request_successful", False)
        log_error_if_needed(
            model="gpt-3.5-turbo",
            error_message=exception._message,  # type: ignore  # pylint: disable=protected-access
            user_prompt=prompt,
            parameters={
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty,
            },
        )

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
write_to_log(__prompt, __response, __jailbreak_prompt if __unlocked else None)
