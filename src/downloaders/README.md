# Information Regarding Article Downloaders

Information regarding when each corpus downloader was run is contained in this
file.

## Corpora Last Access Dates

Corpus | Last Updated
--- | ---
`plos` |
`elsevier` | 2016-03-13 07:12 UTC

---

### PLOS Downloading Information

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
