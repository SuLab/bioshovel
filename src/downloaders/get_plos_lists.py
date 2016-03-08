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
        r = requests.get(url, timeout=2)
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

def parse_text(html_page_string, parse_dict):

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

            dois = parse_text(html_string, {'data-metricsurl': '/plosone/article/metrics'})
            f.write('\n'.join(dois)+'\n')

            # wait a few ms before continuing...
            time.sleep(random.random())

            if i % 1000 == 0:
                print('Getting page {} of {}...'.format(i, page_total))

    print('PLOS ONE DOIs saved to {}'.format(plos_one_output_filename))

def main():

    timestamp = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')
    log_filename = 'get_plos_lists_{}.log'.format(timestamp)
    logging.basicConfig(filename=log_filename,level=logging.WARNING)

    get_plos_one_dois(timestamp)

    print('Log file saved to {}'.format(log_filename))

if __name__ == '__main__':
    main()