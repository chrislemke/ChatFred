"""This module contains the exception handling functions."""

import os
import sys
from datetime import datetime
from typing import Dict, Optional, Union

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import openai

__workflow_data_path = os.getenv("alfred_workflow_data") or os.path.expanduser("~")
__workflow_version = os.getenv("alfred_workflow_version") or "unknown"


def env_value_error_if_needed(
    temperature: float,
    model: str,
    max_tokens: Optional[int],
    frequency_penalty: float,
    presence_penalty: float,
) -> Optional[str]:
    """Checks the environment variables for invalid values."""
    if temperature < 0 or temperature > 2.0:
        return f"🚨 'Temperature' must be ≤ 2.0 and ≥ 0. But you have set it to {temperature}."

    if (
        (model == "text-davinci-003" or model == "gpt-3.5-turbo")
        and max_tokens
        and max_tokens > 4096
    ):
        return "🚨 'Maximum tokens' must be ≤ 4096"

    if (
        model in ["text-ada-001", "text-babbage-001", "text-curie-001"]
        and max_tokens
        and max_tokens > 2048
    ):
        return "🚨 'Maximum tokens' must be ≤ 2048."

    if frequency_penalty < -2.0 or frequency_penalty > 2.0:
        return f"🚨 'Frequency penalty' must be between -2.0 and 2.0. But you have set it to {frequency_penalty}."

    if presence_penalty < -2.0 or presence_penalty > 2.0:
        return f"🚨 'Presence penalty' must be between -2.0 and 2.0. But you have set it to {presence_penalty}."

    return None


def exception_response(error: openai.error) -> str:
    """Returns a response for the given error."""
    if isinstance(error, openai.error.AuthenticationError):
        return "🚨 There seems to be something wrong! Please check your API key."

    if isinstance(error, openai.error.InvalidRequestError):
        if str(error).startswith(
            "Your request was rejected as a result of our safety system"
        ):
            return "🚨 You shouldn't generate such stuff! Your prompt was declined by OpenAI's safety system."
        return "🚨 Hmmm... Something is wrong with your request. Try again later."

    if isinstance(error, openai.error.ServiceUnavailableError):
        return "🚨 Oh no! The server is overloaded or not ready yet."

    if isinstance(error, openai.error.APIError):
        return "🚨 D'oh! The server had an error while processing your request."

    if isinstance(error, openai.error.APIConnectionError):
        return "🚨 There is something fishy with your internet connection. Check your network settings."

    if isinstance(error, openai.error.RateLimitError):
        return "🚨 You have reached the rate limit. Check your settings in your OpenAI dashboard."

    if isinstance(error, openai.error.Timeout):
        return "🚨 The request timed out. Try again later."

    return "🚨 Something went wrong. Try again later."


def log_error_if_needed(
    model: str,
    error_message: str,
    user_prompt: str,
    parameters: Dict[str, Union[str, int, float, Optional[int]]],
) -> None:
    """Logs the error to a `ChatFred_Error.log` if `debug` is set to 1."""

    if not os.path.exists(__workflow_data_path):
        os.makedirs(__workflow_data_path)

    with open(
        f"{__workflow_data_path}/ChatFred_Error.log", "a+", encoding="utf-8"
    ) as log:
        log.write("---")
        log.write(f"\nDate/Time: {str(datetime.now())}\n")
        log.write(f"model: {model}\n")
        log.write(f"workflow_version: {__workflow_version}\n")
        log.write(f"error_message: {error_message}\n")
        log.write(f"user_prompt: {user_prompt}\n")
        for key in parameters:
            log.write(f"{key}: {parameters[key]}\n")


def get_last_error_message() -> str:
    """Returns the last error message from the log file."""
    with open(
        f"{__workflow_data_path}/ChatFred_Error.log", "r", encoding="utf-8"
    ) as log:
        lines = log.readlines()
        lines.reverse()
        error = ""
        for line in lines:
            if line.startswith("error_message:"):
                error = line[14:]
                break

    return error
