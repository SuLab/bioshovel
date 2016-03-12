#!/usr/bin/env python3
"""Download all open access articles in English journals catalogued by Elsevier.

Steps:
1. Query ScienceDirect for all Open Access journals in the biological sciences.

    ScienceDirect categorizes its journals by subject area, while Elsevier's API
    does not. However this returns journals of all languages, while we only want
    English publications.

    We will use the NLM Catalog to determine the language of each journal, and
    query NLM via the journal's ISSN for better accuracy.

2. Determine journal ISSN using Elsevier's sitemap.

    ScienceDirect and Elsevier's API do not agree on which journals are open
    access. To determine the ISSN of each journal, we instead use the Elsevier
    sitemap, since the URL of each journal is its ISSN.

3. Query NLM Catalog to determine language of each journal via ISSN.

    A journal may have multiple publication languages.

4. Determine articles in each English journal.

    Identify the articles published in each English journal via the Elsevier
    sitemap.
"""
import json
import logging
import os
import re
import string

from bs4 import BeautifulSoup
from collections import defaultdict
from itertools import islice
from tqdm import tqdm

from fetch_page import fetch_page
from util import cache
from util import load_if_exist

from web_util import fetch_and_map


#@load_if_exist("../../data/elsevier/bio_journal_titles.txt")
def scrape_journal_titles():
    """Get the journal titles of only open access journals in the life or health
    sciences from ScienceDirect.

    Since the web interface has an annoying scrolling refresh, grab the journal
    titles grouped by starting letter.
    """
    def get_titles(html):
        soup = BeautifulSoup(html, "lxml")
        tags = soup.find_all("li", {"class": "browseimpBrowseRow"})
        return [tag.get("data-title") for tag in tags]

    url = ("http://www.sciencedirect.com/science/journals/"
        "sub/5/18/17/220/22/21/466/23/487/{}/open-access")

    data = {
        letter: url.format(letter)
        for letter in string.ascii_lowercase
    }

    return fetch_and_map(get_titles, data, MAX_CONNECTIONS = 10, MAX_TIMEOUT = 10)


def get_api_key():
    floc = os.path.join("..", "..", "data", "elsevier", "apikey.txt")
    with open(floc, "r") as fin:
        api_key = fin.read().rstrip("\n")

    return api_key


@load_if_exist("../../data/elsevier/all_journal_issns.txt")
def scrape_all_journal_issns():
    """Use the Elsevier sitemap of all publications (books, journals) to
    determine the ISSNs of all journals.
    """
    logger = logging.getLogger(__name__)
    url = "http://api.elsevier.com/sitemap/page/sitemap/{}.html"

    # A small number of journals have two ISSNs, but most have unique ISSNs

    issn = defaultdict(list)
    for letter in tqdm(string.ascii_lowercase):
        error, html = fetch_page(url.format(letter))

        if error is not None:
            logger.warn("Sitemap for {} is broken".format(letter))
        else:
            soup = BeautifulSoup(html, "lxml")
            for href in soup.find_all("a", href = re.compile(r'journals')):
                name = href.text
                link = href["href"]

                # the ISSN with the middle dash removed
                val = link[link.rfind("/") + 1 : link.rfind(".")]
                assert len(val) == 8, "{} has a bas ISSN".format(name)

                issn[name].append("{}-{}".format(val[:4], val[4:]))

    return issn


def get_language(journal_issn):
    """Lookup the publication language of each journal using the NLM catalog."""

    logger = logging.getLogger(__name__)
    def get_nlm_uid(issn):
        url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "nlmcatalog",
            "term": "{}[ISSN]".format(issn),
            "retmode": "json"
        }

        error, json = fetch_page(url, params, rettype = "json")
        if error is not None:
            logger.warn("Error querying NLM Catalog with {}".format(issn))
            return None

        if int(json["esearchresult"]["count"]) == 1:
            return json["esearchresult"]["idlist"][0]

        logger.info("No NLM id for {}".format(issn))
        return None

    def get_nlm_entry(nlm_uid):
        url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            "db": "nlmcatalog",
            "id": nlm_uid
        }

        error, text = fetch_page(url, params)
        assert error is None, "Error for NLM UID {}".format(nlm_uid)

        return text

    nlm_uid = get_nlm_uid(journal_issn)
    if nlm_uid is None:
        return "unknown"

    text = get_nlm_entry(nlm_uid)
    lines = text.split("\n")
    for line in lines:
        if line.startswith("Language:"):
            return line[len("Language: ") : ].split(", ")

    raise Exception("NLM Catalog missing language field for {}".format(journal_issn))


@load_if_exist("../../data/elsevier/open_journal_languages.txt")
def get_languages(journal_titles, issns):
    return {journal: get_language(issns[journal][0])
        for journal in tqdm(journal_titles)
            if journal in issns and len(issns[journal]) == 1
    }


def scrape_piis_in_journal(url):
    """Given the URL of a specific journal, return all the Elsevier PIIs for
    articles in that journal.
    """
    logger = logging.getLogger(__name__)

    def get_next_level(cur_url):
        """Skip the first link because it's self-referential."""
        error, html = fetch_page(cur_url)

        if error is not None:
            logger.warning("Could not access {}".format(cur_url))
            return []

        soup = BeautifulSoup(html, "lxml")
        return [link["href"] for link in islice(soup.find_all("a"), 1, None)]

    def has_pii(links):
        """Are these links to actual articles?"""
        return any("article/pii" in link for link in links)


    links = get_next_level(url)
    if not links:
        logging.warning("No articles for the journal {}".format(url))
        return []

    while not has_pii(links):
        temp = []
        for link in tqdm(links):
            temp += get_next_level(link)

        links = temp

    return links


@load_if_exist("../../data/elsevier/eng_open_bio_journal_piis.txt")
def scrape_all_piis(issns, languages):
    """Scrape the PIIs of all English articles in open access Elsevier journals."""
    url = "http://api.elsevier.com/sitemap/page/sitemap/serial/journals/{}/{}.html"

    piis = dict()
    for journal, langs in languages.items():
        if langs == ["English"]:
            issn = issns[journal]
            assert len(issn) == 1

            link = url.format(journal[0].lower(), issn[0].replace("-", ""))

            piis[journal] = scrape_piis_in_journal(link)

    return piis


def main():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        filename = "../../logs/elsevier_scraper.log",
        level = logging.INFO, format = log_format
    )


    journal_titles = scrape_journal_titles()
    cache("ttt.txt", journal_titles)
    print("done")
    return

    issns = scrape_all_journal_issns()

    lang = get_languages(journal_titles, issns)

    piis = scrape_all_piis(issns, lang)
    print("done")


if __name__ == "__main__":
    main()
