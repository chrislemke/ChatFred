"""This module contains the image generation API."""

import os
import sys
import urllib.request
from datetime import datetime

from caching_manager import read_from_cache, write_to_cache
from custom_prompts import error_prompts
from error_handler import (
    exception_response,
    get_last_error_message,
    log_error_if_needed,
)

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import openai

openai.api_key = os.getenv("api_key")
__size = int(os.getenv("image_size") or 512)


def get_query() -> str:
    """Join the arguments into a query string."""
    return " ".join(sys.argv[1:])


def prepare_file_name(prompt: str) -> str:
    """Prepares the file name."""
    return (
        prompt.replace(" ", "_")
        .replace(",", "")
        .replace(".", "")
        .replace('"', "")
        .replace(":", "")
        .replace("'", "")
        .replace("/", "")
        .replace("\\", "")
    )


def intercept_custom_prompts(prompt: str):
    """Intercepts custom queries."""

    last_request_successful = read_from_cache(
        "last_image_generation_request_successful"
    )
    if prompt in error_prompts and not last_request_successful:
        sys.stdout.write(
            f"😬 Sorry, the error message was not really helpful. Here is the original message from OpenAI:\n\n➡️ {get_last_error_message()}"
        )
        write_to_cache("last_image_generation_request_successful", True)
        sys.exit(0)


def make_request(prompt: str, size: int) -> str:
    """Makes the request to the OpenAI API."""

    datetime_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = f"{os.path.expanduser('~')}/ChatFred_{prepare_file_name(prompt)}_{datetime_string}.png"

    intercept_custom_prompts(prompt)
    write_to_cache("last_image_generation_request_successful", True)

    try:
        response = openai.Image.create(prompt=prompt, n=1, size=f"{size}x{size}")
        urllib.request.urlretrieve(response["data"][0]["url"], file_path)  # nosec
        return file_path

    except Exception as exception:  # pylint: disable=broad-except
        write_to_cache("last_image_generation_request_successful", False)
        log_error_if_needed(
            model="dall_e-2",
            error_message=exception._message,  # type: ignore  # pylint: disable=protected-access
            user_prompt=prompt,
            parameters={
                "size": size,
            },
        )

        return exception_response(exception)


__response = make_request(get_query(), __size)
sys.stdout.write(__response)
