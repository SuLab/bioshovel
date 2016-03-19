# Open Access Article Downloaders

Information regarding when each corpus downloader was run is contained in this
file.

## Corpora Last Access Dates

Corpus | Last Updated
--- | ---
`plos` | 2016-03-11 18:54 UTC
`elife` | 2016-03-08 17:35 UTC
`elsevier` | 2016-03-13 07:12 UTC

---

### PLOS Downloading Information

The PLOS API appears to be nonfunctional at the moment, so we resort to [DOI](https://en.wikipedia.org/wiki/Digital_object_identifier) scraping and XML-format article downloads.

Most of the PLOS journals have journal archive pages with lists of issues, _e.g._, <http://journals.plos.org/plosbiology/volume>

From the list of issues on this page, we can access each issue's Table of Contents (ToC) page, _e.g._, <http://journals.plos.org/plosbiology/issue?id=info%3Adoi%2F10.1371%2Fissue.pbio.v14.i02>

From a ToC page, we can obtain DOIs for all articles in an issue. 

The list of DOIs can then be used to access articles with URLs of the format:
`http://journals.plos.org/plosbiology/article/asset?id=[escaped_DOI]` where `[escaped_doi]` will be a DOI with its forward slash escaped, _e.g._, `10.1371/journal.pbio.1002384.XML` -> `10.1371%2Fjournal.pbio.1002384.XML`

PLOS ONE articles can be accessed in a similar way by first compiling a list of DOIs from the _list view_ of **Biology and life sciences** articles here: <http://journals.plos.org/plosone/browse/biology_and_life_sciences?resultView=list>

### eLife Downloading Information

eLife has made XML versions of their articles available at <https://github.com/elifesciences/elife-articles>

### Elsevier Downloading Information

**Goal:** Download all English open access articles from Elsevier biology journals.

Elsevier provides an exhaustive list of all of its publications at:
<http://api.elsevier.com/sitemap/page/sitemap/index.html>

The sitemap is indexed in a top-down fashion, with articles grouped by journal
and issue. Prior to downloading the actual articles, we need to retrieve
information about their containing journals.

However, the Elsevier sitemap provides no metadata information about the thousands
of journals it indexes. We need another way to determine what is the language,
subject area, and open access status of each journal.

ScienceDirect provides metadata about the journals, but provides no API.

---

#### Document Retrieval Process

All information retrieved on 2016-03-13.

1. Go to [ScienceDirect](http://www.sciencedirect.com)
2. Click "Browse all titles" in the "Browse publications by subject" box.

    This retrieves 28641 publications (all titles, all publication types, all
    access types).

3. Check "Life Sciences" and "Health Sciences" under the "Filter by subject" area.
Click "Apply".

    This retrieves 11412 publications (all titles, all publication types, all
    access types).

4. Select "All journals" from the publication type drop down menu.

    This retrieves 2487 journals (all titles, all access types).

5. Select "Open access journals" from the access type drop down menu.

    This retrieves 332 publications (all titles). The URL should now be:
    http://www.sciencedirect.com/science/journals/sub/5/18/17/220/22/21/466/23/487/all/open-access

6. Accessing each group of journals by starting letter (change "all" to the starting
letter) avoids using the scrolling update function (since the titles all fit onto
one page).

7. The `get_elsevier.py` downloader begins with this step. It retrieves all open
access biology journal titles, determines which are in English using the NLM
Catalog, and then proceeds to download the articles using the Elsevier API.

    Additional details about this process can be found in `get_elsevier.py`
