# Tong Shu Li
"""
Download Elsevier articles.
"""
import os
import re
import string

from bs4 import BeautifulSoup
from collections import defaultdict
from tqdm import tqdm

from fetch_page import fetch_page
from util import load_if_exist

@load_if_exist("../../data/elsevier/bio_journal_titles.txt")
def scrape_journal_titles():
    """Get the journal titles of only open access journals in the life or health
    sciences from ScienceDirect.

    Since the web interface has an annoying scrolling refresh, grab the journal
    titles grouped by starting letter.
    """
    BASE = "http://www.sciencedirect.com/science/journals/"

    journal_titles = []
    for first_letter in tqdm(string.ascii_lowercase):
        query = "sub/5/18/17/220/22/21/466/23/487/{}/open-access".format(first_letter)
        error, html = fetch_page(BASE + query)

        if error is not None:
            print("Could not query {} due to: {}".format(BASE + query, error))
        else:
            soup = BeautifulSoup(html, "lxml")
            tags = soup.find_all("li", {"class": "browseimpBrowseRow"})
            journal_titles += [tag.get("data-title") for tag in tags]

    return journal_titles

def get_api_key():
    floc = os.path.join("..", "..", "data", "elsevier", "apikey.txt")
    with open(floc, "r") as fin:
        api_key = fin.read().rstrip("\n")

    return api_key

def scrape_issn(journal_title):
    url = "http://api.elsevier.com/content/serial/title"

    api_key = get_api_key()

    params = {
        "apiKey": api_key,
        "title": journal_title,
        "httpAccept": "application/xml",
        "content": "journal"
#        "oa": "full"
    }

    error, html = fetch_page(url, params)
    if error is not None:
        print("Could not query {} due to {}".format("{} {}".format(url, params), error))
    else:
        soup = BeautifulSoup(html, "lxml")

        for entry in soup.find_all("entry"):
            titles = entry.find_all("dc:title")
            assert len(titles) == 1
            title = titles[0].text

            if title == journal_title:
                issns = entry.find_all("prism:issn")
                assert len(issns) == 1, "{}".format(journal_title)
                return issns[0].text

    # failed to find the issn of this journal title
    return None

def cache_all_publications():
    url = "http://api.elsevier.com/sitemap/page/sitemap/{}.html"

    pubs = defaultdict(list)
    for letter in tqdm(string.ascii_lowercase):
        error, html = fetch_page(url.format(letter))
        assert error is None, "{}".format(letter)

        soup = BeautifulSoup(html, "lxml")

        for href in soup.find_all("a", href = re.compile(r'journals')):
            name = href.text
            link = href["href"]
            issn = link[link.rfind("/") + 1 : link.rfind(".")]

            pubs[name].append(issn)

    return pubs

def get_issn(journal_title):
    first_char = journal_title[0].lower()

    url = "http://api.elsevier.com/sitemap/page/sitemap/{}.html".format(first_char)

    error, html = fetch_page(url)
    if error is not None:
        print("Could not query {} due to {}".format(url, error))
    else:
        soup = BeautifulSoup(html, "lxml")
        links = soup.find_all("a", href = True, text = journal_title)
        assert len(links) == 1, "{}".format(journal_title)

        link = links[0]["href"]
        issn = link[link.rfind("/") + 1 : link.rfind(".")]
        return issn

    return None

def main():
    titles = scrape_journal_titles()
    print(len(titles))
    return




    journal_titles = get_journal_titles()

    info = cache_all_publications()
    with open("pubs.txt", "w") as fout:
        for name, issns in info.items():
#            assert len(issns) == 1
            fout.write("{}\t{}\n".format(name, issns))

    return

    print("scraping issns")

    issns = []

    with open("out.txt", "w") as fout:
        for title in tqdm(journal_titles):
            issn = get_issn(title)
            issns.append(issn)
            fout.write("{}\t{}\n".format(title, issn))


if __name__ == "__main__":
    main()
