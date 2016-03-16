#!/usr/bin/env python3

# parse_elife_xml.py
#
# usage:
# ./parse_elife_xml.py [xml_directory]
#
# Parses eLife articles in XML format from path
# ../../data/elife/xml/ and extracts DOIs and paragraphs,
# saving them to ../../data/elife/paragraphs
#
#
# Files are saved with filename [extracted_DOI]
# with one paragraph per line, including abstract and
# executive summary, if available

# Sandip Chatterjee

import logging
import os
import re
import sys
from bs4 import BeautifulSoup
from glob import glob
from itertools import chain
from tqdm import tqdm
from unidecode import unidecode

def read_file(file_path):

    ''' Reads in data from an XML file at file_path and returns a BeautifulSoup
        parser object

        Converts any Unicode to ASCII and replaces <body> tags with 
        <bodyreplaced> for better compatibility with lxml parser
    '''

    with open(file_path) as f:
        xml_data = unidecode(f.read())
        
    # replace body tags because they don't work well 
    # with lxml parser
    replacements = (('<body>',  '<bodyreplaced>'),
                    ('</body>', '</bodyreplaced>'),
                   )

    for orig, new in replacements:
        xml_data = xml_data.replace(orig, new)

    # note: `soup` cuts off before the first figure! (only with 'xml' parser 
    # and features='xml'... not with lxml parser)
    return BeautifulSoup(xml_data, 'lxml')

def get_doi(soup, escape_slash=True):

    ''' Given a BeautifulSoup object for an eLife XML article, return the 
        article's DOI (escape the forward slash if necessary)
    '''

    try:
        doi = soup.find('article-id', {'pub-id-type':'doi'}).string
    except AttributeError:

        return ''

    cleaned_doi = clean(doi).lower()

    if escape_slash:
        return cleaned_doi.replace('/', '%2F')
    else:
        return cleaned_doi

def clean(string):

    ''' returns string without newlines and whitespace
    '''

    return string.replace('\n', '').strip()

def get_title(soup):

    ''' Given a BeautifulSoup object for an eLife XML article, return the 
        article's title (return None if no title available)
    '''

    try:
        title = soup.find('article-title').get_text()
        clean_title = clean(title)

        # compress multiple spaces left by auto-unwrapped style tags:
        return ' '.join(clean_title.split())
    except AttributeError:
        logging.warning('No title for article {}'.format(get_doi(soup, 
                                                         escape_slash=False)))
        return None

def get_abstract(soup):

    ''' Given a BeautifulSoup object for an eLife XML article, return the 
        article's abstract (return None if no abstract available)
    '''

    try: 
        abs_string = soup.find('abstract').p.get_text()
        cleaned_abs = clean(abs_string)

        # compress multiple spaces left by auto-unwrapped style tags:
        return ' '.join(cleaned_abs.split())
    except AttributeError:
        logging.warning('No abstract for article {}'.format(
            get_doi(soup, escape_slash=False)))
        return None

def get_exec_summary(soup):

    ''' Given a BeautifulSoup object for an eLife XML article, return the 
        article's executive summary as a list (return None if none available)
    '''

    exec_attrs = {'abstract-type': 'executive-summary'}
    try:
        exec_summary_raw_tags = [tag 
                                 for tag in soup.
                                            find('abstract', exec_attrs).
                                            find_all('p')]
        exec_summary_string_tags = [tag.get_text() 
                                    for tag in exec_summary_raw_tags 
                                    if tag.get_text()]
    except AttributeError:
        logging.warning('No executive summary for article {}'.format(
            get_doi(soup, escape_slash=False)))
        return None

    cleaned_paragraphs = [clean(p) for p in exec_summary_string_tags]
    return remove_doi_lines(cleaned_paragraphs)

def get_paragraphs(article_sections, main_article):

    ''' Given a list of BeautifulSoup section tag objects, return 
        a list of paragraph objects for each section

        Returns a nested list:
        [[section1_paragraph1, section1_paragraph2, ...]
         [section2_paragraph1, section2_paragraph2, ...]]
    '''
    
    if article_sections:
        # normal article
        return [section.find_all('p') for section in article_sections]
    else:
        # not a normal article. probably a correction-type brief "article"
        return [main_article.find_all('p', recursive=False)]

def remove_doi_lines(cleaned_paragraphs):

    ''' Remove figure-specific DOI lines that have
        <p> tags
    '''
    
    return [p for p in cleaned_paragraphs if not p.startswith('DOI')]

def get_main_article(soup, keep_references=True):

    ''' Given a BeautifulSoup object for an eLife XML article, return the 
        article's main text as a list of paragraphs

        keep_references is a flag that can be set to False to remove article and
        figure references from the output paragraphs
    '''

    def unwrap_tag(tag_string, all_paragraphs):
        
        ''' Remove stylistic tags without removing string contents of those tags
        '''
        
        for p in chain(*all_paragraphs):
            for tag in p.find_all(tag_string):
                tag.unwrap()

        # # return value not needed here
        # return all_paragraphs

    def decompose_tag(tag_string, all_paragraphs):

        ''' Remove all trace of tag_string (including text encompassed by tag)
        '''

        for p in chain(*all_paragraphs):
            for tag in p.find_all(tag_string):
                tag.decompose()

    def remove_reference_debris(cleaned_paragraphs):
        
        ''' Remove remaining (), (;), (;;), etc. that is 
            "debris" from running tag.decompose() on xref 
            tags
            
            Also removes figure reference debris, such as
            (,), (-,), (,,-), etc.
        '''

        regex = re.compile(r'(\s+\([;|,|-]*\))')

        return [regex.sub('', p) for p in cleaned_paragraphs]

    def get_cleaned_paragraphs(all_paragraphs):

        ''' Return cleaned, markup-free paragraph text from all_paragraphs
        '''
        
        return [clean(p.get_text(strip=True)) for p in chain(*all_paragraphs)]

    body_tags = soup.find_all('bodyreplaced')
    main_article = body_tags[0]
    # main_article.find_all('p', recursive=False)
    sections = main_article.find_all('sec', recursive=False)

    all_paragraphs = get_paragraphs(sections, main_article)

    for tag in ('bold', 'italic', 'sub', 'sup'):
        unwrap_tag(tag, all_paragraphs)

    if keep_references:
        cleaned_paragraphs = get_cleaned_paragraphs(all_paragraphs)
        cleaned_paragraphs = remove_doi_lines(cleaned_paragraphs)
        if not cleaned_paragraphs:
            logging.critical('No main text paragraphs for {}'.format(get_doi(soup)))
        return cleaned_paragraphs

    for tag in ('xref', 'fig-group', 'caption', 'table-wrap'):
        decompose_tag(tag, all_paragraphs)

    cleaned_paragraphs = get_cleaned_paragraphs(all_paragraphs)
    cleaned_paragraphs = remove_doi_lines(cleaned_paragraphs)
    cleaned_paragraphs = remove_reference_debris(cleaned_paragraphs)

    # remove empty "paragraphs"
    cleaned_paragraphs = [p for p in cleaned_paragraphs if p.strip()]

    if not cleaned_paragraphs:
        logging.critical('No main text paragraphs for {}'.format(get_doi(soup)))

    return cleaned_paragraphs

def save_file(output_file_lines, save_file_path):

    ''' Given a list of tuples output_file_lines, output tab-delimited file to 
        save_file_path

        output_file_lines should have this structure:
        [('title', 'Atomic structure of the 26S proteasome lid'),
         ('abstract', 'abstract_text'),
         (')]
    '''

    with open(save_file_path, 'w') as f:
        for label_line_tuple in output_file_lines:
            f.write('\t'.join(label_line_tuple)+'\n')

def main():

    xml_directory = sys.argv[1]
    save_directory = os.path.join(xml_directory, '../paragraphs')

    # check if save_directory exists and create if necessary
    if not os.path.isdir(save_directory):
        os.makedirs(save_directory)

    xml_files = glob(os.path.join(xml_directory, '*.xml'))

    for file_path in tqdm(xml_files):

        output_file_lines = []

        soup = read_file(file_path)
        
        escaped_doi = get_doi(soup)
        if not escaped_doi:
            logging.critical('No DOI found in {}'.format(file_path))
            continue
        logging.warning('Processing {}'.format(escaped_doi))
        
        title = get_title(soup)
        if not title:
            logging.critical('No title for {}'.format(file_path))
        else:
            output_file_lines.append(('title', title))
        
        abstract = get_abstract(soup)
        if abstract:
            output_file_lines.append(('abs', abstract))

        exec_summary = get_exec_summary(soup)
        if exec_summary:
            for paragraph in exec_summary:
                output_file_lines.append(('p', paragraph))

        article_paragraphs = get_main_article(soup, keep_references=False)

        for paragraph in article_paragraphs:
            output_file_lines.append(('p', paragraph))

        save_file(output_file_lines, os.path.join(save_directory, escaped_doi))

    logging.warning('All finished')

if __name__ == '__main__':
    assert len(sys.argv) == 2, 'Need an XML directory'

    log_dir = '../../logs'
    log_filename = os.path.join(log_dir, 'parse_elife_xml.log')
    logging.basicConfig(filename=log_filename, 
                        level=logging.WARNING,
                        filemode='w') # overwrite logfile on each run

    main()