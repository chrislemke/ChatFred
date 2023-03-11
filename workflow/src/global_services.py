"""This module contains the global services used by the workflow."""

import os
import plistlib
from typing import Union

__workflow_data_path = os.getenv("alfred_workflow_data") or os.path.expanduser("~")
__cache_file_path = f"{__workflow_data_path}/ChatFred_Cache"


def write_to_cache(key: str, value: Union[str, int, float, bool]) -> None:
    """Writes the user input and the assistant output to the log file."""

    if not os.path.exists(__workflow_data_path):
        os.makedirs(__workflow_data_path)

    data = None
    if os.path.exists(__cache_file_path):
        with open(__cache_file_path, "rb") as plist:
            data = plistlib.load(plist)

            if data.get(key):
                data[key] = value
            else:
                data[key] = value
    else:
        data = {key: value}

    if data:
        with open(__cache_file_path, "wb") as plist:
            plistlib.dump(data, plist)


def read_from_cache(entry: str) -> Union[str, int, float, bool, None]:
    """Reads the cache file and returns the value of the entry."""

    if os.path.exists(__cache_file_path):
        with open(__cache_file_path, "rb") as plist:
            data = plistlib.load(plist)
        return data.get(entry)
    else:
        return False
