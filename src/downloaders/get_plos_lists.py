#!/usr/bin/env python3

# get_plos_lists.py
#
# For getting PLOS DOIs from the plos.org website

from bs4 import BeautifulSoup
from datetime import datetime
import logging
import random
import requests
import sys
import time

def get_single_page(url):

    ''' Get url with requests. Return HTML text if
        successful or False if unsuccessful
    '''

    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.text
    except requests.exceptions.ConnectionError:
        logging.error('Requests ConnectionError: {}'.format(url))
    except requests.exceptions.Timeout:
        logging.error('Requests Timeout: {}'.format(url))
    except requests.exceptions.HTTPError:
        logging.error('Requests HTTPError: {}'.format(url))
    except:
        logging.error('Unknown error: {}'.format(url))

    return False

def get_html(url):

    ''' Try to get a proper HTML response up to 
        3 times with random delays in between. 

        If unsuccessful, report failure.
    '''

    requests_remaining = 3
    while requests_remaining > 0:
        r = get_single_page(url)
        if r:
            return r
        requests_remaining -= 1
        time.sleep(random.random())

    logging.critical('URL get_html failed after 3 attempts: {}'.format(url))
    return False

def parse_text_plos_one(html_page_string, parse_dict):

    ''' Parse HTML page with BeautifulSoup.

        Look for HTML tags that have this format:
        <li data-doi="10.1371/journal.pone.0151074" 
        data-pdate="2016-03-07T00:00:00Z" 
        data-metricsurl="/plosone/article/metrics">

        Return a list of DOIs (empty if none found.
    '''

    if not html_page_string: # if empty string or False
        return []

    soup = BeautifulSoup(html_page_string, 'html.parser')

    matches = soup.find_all('li', parse_dict)
    if not matches:
        logging.error('parse error (no matches found)')

    return [match.get('data-doi') for match in matches]

def get_plos_one_dois(timestamp):

    ''' Loop over entire range of PLOS ONE
        index pages ('Biology and Life Sciences' section)

        Parse HTML and write DOIs to file.
        (PLOS ONE pages have a format different from 
         other PLOS journals...)
    '''

    plos_one_output_filename = 'plos_one_dois_{}.txt'.format(timestamp)

    with open(plos_one_output_filename, 'w') as f:

        # as of 3/7/16, PLOS One list view for Biological 
        # Sciences articles goes up to 10909 "list" pages
        page_total = 10909
        for i in range(1,page_total+1):
            base_url = 'http://journals.plos.org/plosone/browse/biology_and_life_sciences?resultView=list&page={}'
            html_string = get_html(base_url.format(i))

            dois = parse_text_plos_one(html_string, {'data-metricsurl': '/plosone/article/metrics'})
            f.write('\n'.join(dois)+'\n')

            # wait a few ms before continuing...
            time.sleep(random.random())

            if i % 1000 == 0:
                print('Getting page {} of {}...'.format(i, page_total))

    print('PLOS ONE DOIs saved to {}'.format(plos_one_output_filename))

def get_issue_urls(journal_archive_url):

    ''' Accesses and parses journal_archive_url
        and returns a list of URLs for each issue
        (for all PLOS journals except PLOS ONE)
    '''

    html_string = get_html(journal_archive_url)
    if not html_string: # if empty string or False
        return []

    soup = BeautifulSoup(html_string, 'html.parser')

    journal_slides_ul = soup.find('ul', {'id': 'journal_slides'})
    if not journal_slides_ul:
        logging.critical('failed to parse issue URL: {}'.format(journal_archive_url))
        return

    all_links = journal_slides_ul.find_all('a')

    base_url = 'http://journals.plos.org'
    return [base_url+a_tag['href'] for a_tag in all_links]

def get_issue_dois(issue_url):

    ''' Given an issue_url, return a list of all DOIs
        from that journal issue
        (for all PLOS journals except PLOS ONE)
    '''

    html_string = get_html(issue_url)
    if not html_string: # if empty string or False
        return []

    soup = BeautifulSoup(html_string, 'html.parser')
    matches = soup.find_all('p', {'class': 'article-info'})

    return [match.text.split('|')[1].strip() for match in matches]

def get_plos_dois(timestamp, journal_abbrev):

    ''' For use with all PLOS journals except PLOS ONE.

        Loops over range of journal issues from Volume 1 
        to Volume num_volumes, starting with issue 
        start_month (first issue month of first volume)
        and ending with issue end_month (latest issue month
        of latest volume)

        Parses HTML and writes DOIs to file based on journal_abbrev.
        (journal_abbrev appears in the URL for each journal page)
    '''

    journal_archive_url = 'http://journals.plos.org/{}/volume'.format(journal_abbrev)
    issue_urls = get_issue_urls(journal_archive_url)

    if not issue_urls:
        return

    output_filename = '{}_dois_{}.txt'.format(journal_abbrev, timestamp)
    with open(output_filename, 'w') as f:
        for issue_url in issue_urls:
            time.sleep(random.random())
            f.write('\n'.join(get_issue_dois(issue_url))+'\n')

    return output_filename

def main():

    timestamp = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')
    log_filename = 'get_plos_lists_{}.log'.format(timestamp)
    logging.basicConfig(filename=log_filename,level=logging.WARNING)

    for plos_journal in ('plosbiology',
                         'ploscompbiol',
                         'plosgenetics',
                         'plosmedicine',
                         'plosntds',
                         'plospathogens'):
        output_filename = get_plos_dois(timestamp, plos_journal)
        if output_filename:
            print('{} DOIs saved to {}'.format(plos_journal, output_filename))

    get_plos_one_dois(timestamp)

    print()
    print('Log file saved to {}'.format(log_filename))

if __name__ == '__main__':
    main()