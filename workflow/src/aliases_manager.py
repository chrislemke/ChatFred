"""This module contains the aliases manager for the workflow."""

import os
from typing import Dict

__aliases = os.getenv("cf_aliases")


def __prepare_aliases() -> Dict[str, str]:
    """Prepares the aliases for the workflow.

    Returns:
        Dict[str, str]: A dictionary containing the aliases.
    """
    aliases_dict = {}
    aliases = [alias_list.split("=") for alias_list in str(__aliases).split(";")]
    for alias in aliases:
        if len(alias) == 2:
            aliases_dict[alias[0].replace("\n", "")] = alias[1].replace("\n", "")
    return aliases_dict


def prompt_for_alias(prompt: str) -> str:
    """Returns the prompt for the provided alias. If the alias is not found, it
    returns the provided original prompt.

    Args:
        prompt (str): The prompt to be checked for an alias.

    Returns:
        str: The prompt for the provided alias, or the original prompt if the alias is not found.
    """
    aliases_dict = __prepare_aliases()

    for k, v in aliases_dict.items():
        prompt = prompt.replace(k, v)
    
    return prompt
