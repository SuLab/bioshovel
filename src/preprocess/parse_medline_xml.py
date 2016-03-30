#!/usr/bin/env python3
'''
parse_medline_xml.py

Parses article abstracts from MEDLINE XML files (can be gzipped)

Run `python3 -m preprocess.parse_medline_xml -h` for options
'''

import argparse
import gzip
import os
from glob import glob
from lxml import etree
from tqdm import tqdm
from unidecode import unidecode
from preprocess.util import (ensure_path_exists,
                             file_exists_or_exit,
                             save_file)

def get_root_object(filepath):

    ''' Given a filepath to an XML file (optionally gzipped), return the file's 
        lxml root object
    '''

    if filepath.endswith('.gz'):
        with gzip.open(filepath, 'rb') as f:
            tree = etree.parse(f)
    else:
        with open(filepath) as f:
            tree = etree.parse(f)

    root = tree.getroot()

    return root

def get_element(element_name, element_tag):

    ''' Given an XML element_name (string) and an element tag, return a list of 
        all elements matching element_name within the element (recursive)
    '''

    return list(element_tag.iter(element_name))

def get_abstract_parent_info(abstract):

    ''' Given an lxml AbstractText tag object, return a dict with keys corresponding
        to the abstract's parent articles etc
    '''
    
    parent_abstract = abstract.getparent()
    parent_article = parent_abstract.getparent()
    parent_citation = parent_article.getparent()
    parent_citation_set = parent_citation.getparent()
    has_pmid = parent_citation.find('PMID')
    has_title = parent_article.find('ArticleTitle')

    if has_pmid is not None:
        pmid = has_pmid.text
    else:
        pmid = None

    if has_title is not None:
        title = has_title.text
    else:
        title = None

    info_dict = {}
    info_dict['abstract_text'] = abstract.text
    info_dict['parent_abstract'] = parent_abstract
    info_dict['parent_article'] = parent_article
    info_dict['parent_citation'] = parent_citation
    info_dict['parent_citation_set'] = parent_citation_set
    info_dict['pmid'] = pmid
    info_dict['title'] = title

    return info_dict

def combine_all_abstract_text_tags(abstract_tag_element):

    ''' Given an lxml abstract_tag_element, return a string representing all 
        sentences in the abstract
    '''

    return ' '.join(l.text for l in abstract_tag_element.iter('AbstractText')
                           if l.text)
    # need to check that l.text returns a value (l.text may be None in the case
    # of self-closing AbstractText tags... see PMID 17687753)

def create_filelines(title, abstract):

    ''' Create parform filelines (with newlines) from input strings

        Run unidecode to remove/replace unicode characters.
    '''

    file_lines = []
    file_lines.append('\t'.join(('title', title)))
    file_lines.append('\t'.join(('abs', abstract)))

    return [unidecode(line+'\n') for line in file_lines]

def create_pmid_doi_mapping(args, escape_slash=True):

    ''' Returns a dictionary that maps PMIDs (strings) to DOIs (strings)
    '''

    pmid_doi_map = {}

    if not args.doiindex:
        return pmid_doi_map

    print('Reading PMC ID mapping file')
    with open(args.doiindex) as f:
        for line in tqdm(f):
            line_split = line.split(',')
            pmid_column = line_split[9]
            doi_column = line_split[7]
            if doi_column and pmid_column:
                pmid_doi_map[pmid_column] = doi_column.replace('/','%2F')

    return pmid_doi_map

def main(args):

    ensure_path_exists(args.output_directory)
    pmid_path = os.path.join(args.output_directory, 'by_pmid')
    ensure_path_exists(pmid_path)

    if args.doiindex:
        file_exists_or_exit(args.doiindex)
        doi_path = os.path.join(args.output_directory, 'by_doi')
        ensure_path_exists(doi_path)

    pmid_doi_map = create_pmid_doi_mapping(args)

    all_files = glob(os.path.join(args.xml_file_directory, '*'))
    doi_filenames = []
    pmid_filenames = []
    skipped_files = 0

    print('Processing {} XML files...'.format(len(all_files)))
    for xml_filepath in tqdm(all_files):
        root = get_root_object(xml_filepath)
        citations = get_element('MedlineCitation', root)

        for citation in citations:

            abstracts = get_element('AbstractText', citation)
            if not abstracts: # not all MedlineCitations have Abstracts...
                continue

            # grab one of the abstracts identified in this citation and identify
            # its parent XML elements
            first_abstract_section = abstracts[0]
            d = get_abstract_parent_info(first_abstract_section)

            pmid = d['pmid']
            title = d['title']
            if not pmid or not d['title']:
                # if no PMID, no easy way to identify article (skip)
                # if no title, nothing to include in PubTator title line (skip)
                skipped_files += 1
                continue

            combined_abstract = combine_all_abstract_text_tags(d['parent_abstract'])
            file_lines = create_filelines(title, combined_abstract)

            doi_file_name = pmid_doi_map.get(pmid)
            if doi_file_name:
                # use DOI file name and file path
                doi_filenames.append(save_file(doi_file_name, file_lines, doi_path))
            else:
                # use PMID file name and file path
                pmid_filenames.append(save_file(pmid, file_lines, pmid_path))

    print('{} files saved by PMID to {}'.format(len(pmid_filenames), pmid_path))
    if args.doiindex:
        print('{} files saved by DOI to {}'.format(len(doi_filenames),
                                                   doi_path))
    print('{} MEDLINE citations skipped'.format(skipped_files))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parses article abstracts from MEDLINE XML files')
    parser.add_argument('xml_file_directory', help='Directory of MEDLINE XML files')
    parser.add_argument('output_directory', help='Output directory for parsed files')
    parser.add_argument('--doiindex', help='Map PMIDs to DOIs, if possible (specify path to PMC ID mapping file PMC-ids.csv)')
    args = parser.parse_args()
    main(args)