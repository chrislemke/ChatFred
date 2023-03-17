"""Custom prompts for custom actions."""

import os
import sys

from caching_manager import read_from_cache

error_prompts = [
    "wtf",
    "what does that even mean?",
    "what does that even mean",
    "shut up and tell me what this means",
    "tell me what this means",
    "show error",
    "show openai error",
    "show OpenAI error",
]

clear_log_prompts = [
    "clear log",
    "clear history",
    "clear chat",
    "clear chat log",
    "delete history",
    "delete log",
    "erase log",
    "forget me",
    "forget everything",
    "forget everything i said",
    "forget everything i said to you",
    "remove log",
    "remove history",
    "remove chat",
    "remove chat log",
]


def set_env_variable() -> None:
    """Sets the environment variable 'user_prompt' to '0' if it is not already
    set.

    If 'user_prompt' is set to an error prompt and the last chat request
    was unsuccessful, or if 'user_prompt' is set to a clear log prompt,
    prints '1' to stdout. Otherwise, prints '0' to stdout.
    """
    prompt = os.getenv("user_prompt") or "0"
    if (
        prompt in error_prompts and not read_from_cache("last_chat_request_successful")
    ) or (prompt in clear_log_prompts):
        sys.stdout.write("1")
    else:
        sys.stdout.write("0")
