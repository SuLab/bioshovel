# Tong Shu Li

import json
import os
import pytz

from datetime import datetime

def cache(file_loc, data):
    """Save the data object to disk as a JSON file."""
    cur_time = datetime.now(pytz.utc)
    timestamp = cur_time.strftime("%Y-%m-%d %H:%M %Z")

    result = {"timestamp": timestamp, "data": data}
    with open(file_loc, "w") as fout:
        json.dump(result, fout, indent = 4)

def load_if_exist(file_loc):
    """Load the function's output if it has already been cached to file.

    Given a function, we first check to see if the results have already been
    cached to disk, and return the cached version if it exists. If the cached
    file doesn't exist, then create it after calling our function.

    The JSON cache contains a timestamp, but does not return the timestamp.
    """
    file_loc = os.path.abspath(file_loc)
    def decorator(function):
        def wrapper(*args, **kwargs):
            if os.path.isfile(file_loc):
                with open(file_loc, "r") as fin:
                    data = json.load(fin)

                return data["data"]

            data = function(*args, **kwargs)
            cache(file_loc, data)
            return data

        return wrapper

    return decorator
