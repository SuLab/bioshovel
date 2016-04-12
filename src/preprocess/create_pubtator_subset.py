#!/usr/bin/env python3
''' create_pubtator_subset.py

    for creating a subset of the pubtator bioconcepts2pubtator_offsets
    download file based on PMIDs in an input file

    creates a directory with pubtator annotations (abstract+offset) saved with
    one abstract per file

    creates another directory with only the abstracts saved in parsed/paragraph
    format for use with other bioshovel.preprocess modules
'''

import argparse
import os
import sys
from pathlib import Path
from tqdm import tqdm

from preprocess.reformat import (pubtator_to_parform,)
from preprocess.util import (ensure_path_exists,
                             file_exists_or_exit,
                             get_file_lines_set,
                             save_file)

def produce_records(bioconcepts_file_path):

    ''' Generator function that produces one record at a time from a large
        (tens of gigabytes) bioconcepts2pubtator_offsets file
    '''

    with open(bioconcepts_file_path) as f:
        record_chunk = []
        for line in f:
            stripped = line.rstrip('\n')
            if stripped:
                record_chunk.append(stripped)
            else:
                yield record_chunk
                record_chunk = []

def main(args):

    file_exists_or_exit(args.pmid_file)
    file_exists_or_exit(args.bioconcepts_file)
    pmids_set = get_file_lines_set(args.pmid_file)

    records = produce_records(args.bioconcepts_file)
    print('Found {} distinct PMIDs in file {}'.format(len(pmids_set),
                                                      args.bioconcepts_file))

    if not args.c:
        # create output subdirectories
        ensure_path_exists(args.output_directory)

        pubtator_outdir = os.path.join(args.output_directory, 'pubtator')
        ensure_path_exists(pubtator_outdir)
        abstract_outdir = os.path.join(args.output_directory, 'abstracts')
        ensure_path_exists(abstract_outdir)

    found_count = 0
    not_found_count = 0
    for record in tqdm(records):
        title, abstract, *ner_lines = record
        pmid = title.split('|')[0]
        if pmid in pmids_set:
            found_count += 1
            if not args.c:
                save_file(pmid,
                          [line+'\n' for line in (title, abstract)],
                          pubtator_outdir)
                _, parform_output = pubtator_to_parform(title,
                                                        abstract,
                                                        newlines=True)
                save_file(pmid, parform_output, abstract_outdir)
        else:
            not_found_count += 1

    print('Out of {} abstracts...'.format(found_count+not_found_count))
    print('- {} records in {}'.format(found_count, args.pmid_file))
    print('- {} records NOT in {}'.format(not_found_count, args.pmid_file))
    if not args.c:
        print('Parsed/paragraph abstracts saved to {}'.format(abstract_outdir))
        print('NER-annotated abstracts saved to {}'.format(pubtator_outdir))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates a subset of the PubTator offsets download based on a list of PMIDs from an input file')
    parser.add_argument('pmid_file', help='File of PMIDs to match')
    parser.add_argument('bioconcepts_file', help='PubTator bioconcepts2pubtator_offsets download file')
    parser.add_argument('output_directory', help='Final output directory')
    parser.add_argument('-c', help='Count # PMIDs matching and exit', action='store_true')
    args = parser.parse_args()
    main(args)