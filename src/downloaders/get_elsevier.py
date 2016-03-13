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
from itertools import chain
from itertools import islice
from tqdm import tqdm

from fetch_page import fetch_page
from util import cache
from util import load_if_exist

from web_util import fetch_and_map


@load_if_exist("../../data/elsevier/bio_journal_titles.txt")
def scrape_journal_titles():
    """Get the journal titles of only open access journals in the life or health
    sciences from ScienceDirect.

    Since the web interface has an annoying scrolling refresh, grab the journal
    titles grouped by starting letter.
    """
    def get_titles(key, html):
        soup = BeautifulSoup(html, "lxml")
        tags = soup.find_all("li", {"class": "browseimpBrowseRow"})
        return [tag.get("data-title") for tag in tags]

    url = ("http://www.sciencedirect.com/science/journals/"
        "sub/5/18/17/220/22/21/466/23/487/{}/open-access")

    data = {
        letter: (url.format(letter), None)
        for letter in string.ascii_lowercase
    }

    info = fetch_and_map(get_titles, data, MAX_CONNECTIONS = 10, MAX_TIMEOUT = 10)
    return sorted(chain.from_iterable(info.values()))


@load_if_exist("../../data/elsevier/all_journal_issns.txt")
def scrape_all_journal_issns():
    """Use the Elsevier sitemap of all publications (books, journals) to
    determine the ISSNs of all journals.
    """
    # A small number of journals have two ISSNs, but most have unique ISSNs
    def get_issns(key, html):
        issn = defaultdict(list)

        soup = BeautifulSoup(html, "lxml")
        for href in soup.find_all("a", href = re.compile(r'journals')):
            name = href.text
            link = href["href"]

            # the ISSN with the middle dash removed
            val = link[link.rfind("/") + 1 : link.rfind(".")]
            assert len(val) == 8, "{} has a bad ISSN".format(name)

            issn[name].append("{}-{}".format(val[:4], val[4:]))

        return issn

    url = "http://api.elsevier.com/sitemap/page/sitemap/{}.html"
    data = {
        letter: (url.format(letter), None)
        for letter in string.ascii_lowercase
    }

    info = fetch_and_map(get_issns, data, MAX_CONNECTIONS = 8)
    res = {}
    for val in info.values():
        res.update(val)

    return res


@load_if_exist("../../data/elsevier/english_journals.txt")
def get_open_eng_bio_journals():
    """Return a dictionary of all English language biological science journals
    that are open access, along with their ISSNs.
    """
    def get_journals():
        titles = scrape_journal_titles()
        issns = scrape_all_journal_issns()
        return {
            title: issns[title][0]
            for title in titles
                if title in issns and len(issns[title]) == 1
        }

    def get_nlm_uid(key, json):
        if int(json["esearchresult"]["count"]) == 1:
            return json["esearchresult"]["idlist"][0]

        logger = logging.getLogger(__name__)
        logger.warn("No NLM catalog UID for {} using ISSN for lookup".format(key))
        return None

    def get_language(key, text):
        for line in text.split("\n"):
            if line.startswith("Language:"):
                return list(set(line[len("Language: ") : ].split(", ")))

        raise Exception("NLM Catalog missing language field for {}".format(key))


    journals = get_journals()

#-------------------------------------------------------------------------------

    # look up the NLM catalog UIDs for each open journal with a unique ISSN
    url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    data = {
        title: (url, {
            "db": "nlmcatalog",
            "term": "{}[ISSN]".format(issn),
            "retmode": "json"
        })
        for title, issn in journals.items()
    }

    nlm_uids = fetch_and_map(get_nlm_uid, data, rettype = "json", MAX_CONNECTIONS = 8)

    # look up the language of each open journal with a NLM identifier
    url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    data = {
        title: (url, {"db": "nlmcatalog", "id": uid})
        for title, uid in nlm_uids.items() if uid is not None
    }

    langs = fetch_and_map(get_language, data, MAX_CONNECTIONS = 8)

    # filter and return only those which are english
    return sorted(title for title, lang in langs.items() if lang == ["English"])


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

    eng_journals = get_open_eng_bio_journals()

    print("done")


if __name__ == "__main__":
    main()
