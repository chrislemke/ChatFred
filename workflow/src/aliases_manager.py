"""This module contains the aliases manager for the workflow."""

import os
from typing import Dict

__aliases = os.getenv("cf_aliases")


def __prepare_aliases() -> Dict[str, str]:
    """Prepares the aliases for the workflow.

    And returns them as a dictionary
    """

    aliases_dict = {}
    aliases = [alias_list.split("=") for alias_list in str(__aliases).split(";")]
    for alias in aliases:
        if len(alias) == 2:
            aliases_dict[alias[0].replace("\n", "")] = alias[1].replace("\n", "")
    return aliases_dict


def prompt_for_alias(prompt: str) -> str:
    """Returns the prompt for the provided alias.

    If the alias is not found, it returns the provided original prompt.`
    """

    aliases_dict = __prepare_aliases()
    if prompt in aliases_dict:
        return aliases_dict[prompt]
    return prompt
