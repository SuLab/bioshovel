#!/usr/bin/env python3
"""Asynchronous webscraping helpers."""
import aiohttp
import asyncio
import logging

from tqdm import tqdm


@asyncio.coroutine
def fetch_page(key, semaphore, url, params = None, rettype = "text",
    MAX_RETRIES = 3, MAX_TIMEOUT = 5, RETRY_WAIT_TIME = 0.1, *args, **kwargs):
    """Fetch a webpage asynchronously and return the result.

    Results are indexed by a unique key.
    """
    with (yield from semaphore): # limit number of concurrent requests
        for i in range(MAX_RETRIES):
            with aiohttp.Timeout(MAX_TIMEOUT), aiohttp.ClientSession() as session:
                try:
                    resp = yield from session.get(url, params = params)

                    if rettype == "text":
                        return (key, (yield from resp.text(encoding = "utf-8")))
                    else:
                        return (key, (yield from resp.json()))

                except Exception as exc:
                    logger = logging.getLogger(__name__)
                    logger.warn("Failed to fetch {}:{}({}) on try #{}/{}: {}".format(
                        key, url, params, i+1, MAX_RETRIES, str(exc)
                    ))

                    yield from asyncio.sleep(RETRY_WAIT_TIME)

        return (key, None)


def fetch_and_map(function, data, MAX_CONNECTIONS = 4, *args, **kwargs):
    """Asychronously fetch and apply a function to the content of a dictionary
    of URLs.

    Results are returned as a dictionary. Args and kwargs are passed to the
    fetch_page() function to set the HTML request parameters.

    Input: F = function(), data = {key: (url, params)}
    Returns: {key: F(fetch_url(url))}
    """

    @asyncio.coroutine
    def process(semaphore):
        tasks = [
            fetch_page(key, semaphore, url, params = params, *args, **kwargs)
            for key, (url, params) in data.items()
        ]

        res = {}
        for coroutine in tqdm(asyncio.as_completed(tasks), total = len(tasks)):
            key, val = yield from coroutine

            if val is not None:
                res[key] = function(key, val)
            else:
                logger = logging.getLogger(__name__)
                logging.warn("Could not process {}:{}".format(key, data[key]))

        return res

    # using asyncio.get_event_loop() means it grabs the main event loop, which,
    # when closed, stops all other event loops from working
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    semaphore = asyncio.Semaphore(MAX_CONNECTIONS, loop = loop)
    res = loop.run_until_complete(process(semaphore))
    loop.close()

    return res
