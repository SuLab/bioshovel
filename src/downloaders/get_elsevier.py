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

5. Download the articles using Elsevier's API.
"""
import logging
import os
import re
import string

from bs4 import BeautifulSoup
from collections import Counter
from collections import defaultdict
from itertools import chain
from itertools import islice

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

    return {
        title: journals[title]
        for title, lang in langs.items() if lang == ["English"]
    }


@load_if_exist("../../data/elsevier/open_english_bio_articles.txt")
def find_articles(journals):
    """Find the article links of the given list of journals."""

    def are_piis(links):
        """Are these links to actual articles?"""
        return all("article/pii" in link for link in links)

    # find the volumes/issues in each journal
    def get_links(key, html):
        """Skip the first link because it's self-referential."""
        soup = BeautifulSoup(html, "lxml")
        return [link["href"] for link in islice(soup.find_all("a"), 1, None)]

    url = "http://api.elsevier.com/sitemap/page/sitemap/serial/journals/{}/{}.html"
    data = {
        title: (url.format(title[0].lower(), issn.replace("-", "")), None)
        for title, issn in journals.items()
    }

    issues = fetch_and_map(get_links, data, MAX_CONNECTIONS = 8)

#-------------------------------------------------------------------------------

    articles = {}
    for journal, links in issues.items():
        data = {link: (link, None) for link in links}

        res = fetch_and_map(get_links, data, MAX_CONNECTIONS = 8)

        temp = sorted(chain.from_iterable(res.values()))
        assert are_piis(temp), "{}'s articles are >2 links deep".format(journal)
        articles[journal] = temp

    return articles


def get_elsevier_apikey():
    floc = os.path.abspath("../../data/elsevier/apikey.txt")
    with open(floc, "r") as fin:
        return fin.read().rstrip("\n")


def download_articles(article_urls, data_type):
    """Download the actual articles from Elsevier and save to disk.

    In order to provide accurate statistics about how many articles were
    successfully downloaded, the list of article URLs should be unique!

    :param: article_urls = List of strings
    :param: data_type in ["xml", "txt"]
    """
    # Elsevier only gives two possibilities, a plain UTF-8 string or XML
    assert data_type in ["xml", "txt"], "Incorrect Elsevier download format!"
    assert len(set(article_urls)) == len(article_urls), "URLs are not unique!"

    def get_PII(article_link):
        """Extract the PII of an article from its link."""
        return article_link[article_link.rfind("/") + 1 : ]

    def get_fname(article_url):
        """Get the filename of the place where we will store the article."""
        return os.path.abspath(
            os.path.join("../../data/elsevier/articles/{}".format(data_type),
            "{}.{}".format(get_PII(article_url), data_type))
        )

    def get_saver(data_type):
        def save_article(key, html):
            try:
                with open(key, "w") as fout:
                    if data_type == "txt":
                        fout.write("{}\n".format(html))
                    else:
                        fout.write("{}\n".format(BeautifulSoup(html, "lxml").prettify()))

                return True
            except Exception as exc:
                logger = logging.getLogger("__name__")
                logger.warn("Fetched {} but failed to save to disk: {}".format(key, str(exc)))
                return False

        return save_article

    params = {
        "httpAccept": "text/{}".format("xml" if data_type == "xml" else "plain"),
        "APIKey": get_elsevier_apikey()
    }

    data = {
        get_fname(url): (url, params)
        for url in article_urls
    }

    # seems like the max speed of retrieving files is 2 articles / second
    res = fetch_and_map(get_saver(data_type), data, MAX_CONNECTIONS = 8)

    logger = logging.getLogger(__name__)
    logger.info("Successfully downloaded {} of {} articles".format(
        Counter(res.values())[True], len(article_urls))
    )

    return res


def main():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        filename = "../../logs/elsevier_scraper.log",
        level = logging.INFO, format = log_format
    )

    logger = logging.getLogger("__name__")
    logger.info("Starting Elsevier Open Access Biological corpus scraper")


    eng_journals = get_open_eng_bio_journals()
    logger.info("Finished filtering journals to English ones only")

    articles = find_articles(eng_journals)
    logger.info("Finished finding article links")

    docset = list(chain.from_iterable(articles.values()))

    data_type = "xml"
    logger.info("Beginning to retrieve {} documents (type: {})".format(len(docset), data_type))
    download_articles(docset, data_type)

    logger.info("Elsevier scraper completed successfully with no errors")


if __name__ == "__main__":
    main()
