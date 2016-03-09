# Tong Shu Li

import requests
import sys
from time import sleep

def fetch_page(url, params = None, rettype = "text",
    MAX_RETRIES = 3, MAX_TIMEOUT = 5, RETRY_WAIT_TIME = 0.1):
    """Fetch the HTML of a URL.

    Returns a tuple:
        (error, html)
        Error will contain a string of the error type, html contains the webpage.
    """
    assert isinstance(url, str), "URL is not a string!"
    assert rettype in ["text", "json"]

    for i in range(MAX_RETRIES):
        try:
            resp = requests.get(url, params = params, timeout = MAX_TIMEOUT)
            # raise an exception if there was a problem
            resp.raise_for_status()
            resp.encoding = "utf-8"
            return (None, resp.text if rettype == "text" else resp.json())
        except requests.exceptions.HTTPError as e:
            # URL is bad, so no sense in trying again
            return ("HTTPError: {}".format(e), None)
        except:
            # keep the last error we had
            error = sys.exc_info()[0]
            sleep(RETRY_WAIT_TIME)
            continue

    return (error, None)
