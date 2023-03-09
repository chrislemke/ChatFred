"""This module contains the image generation API."""

import os
import sys
import urllib.request
from datetime import datetime

from error_handling import exception_response, log_error_if_needed

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import openai

openai.api_key = os.getenv("api_key")
__size = int(os.getenv("image_size") or 512)
__workflow_data_path = os.getenv("alfred_workflow_data") or os.path.expanduser("~")
__workflow_version = os.getenv("alfred_workflow_version") or "unknown"
__debug = int(os.getenv("alfred_debug") or 0)


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


def make_request(prompt: str, size: int) -> str:
    """Makes the request to the OpenAI API."""

    datetime_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = f"{os.path.expanduser('~')}/ChatFred_{prepare_file_name(prompt)}_{datetime_string}.png"

    try:
        response = openai.Image.create(prompt=prompt, n=1, size=f"{size}x{size}")
        urllib.request.urlretrieve(response["data"][0]["url"], file_path)  # nosec
        return file_path

    except Exception as exception:  # pylint: disable=broad-except
        log_error_if_needed(
            model="dall_e-2",
            error_message=exception._message,  # type: ignore  # pylint: disable=protected-access
            user_prompt=prompt,
            parameters={
                "size": size,
            },
            workflow_data_path=__workflow_data_path,
            workflow_version=__workflow_version,
            debug=__debug,
        )

        return exception_response(exception)


__response = make_request(get_query(), __size)
sys.stdout.write(__response)
