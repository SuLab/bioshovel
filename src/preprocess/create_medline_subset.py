#!/usr/bin/env python3
''' create_medline_subset.py

    for creating a subset of medline based on a list of PMIDs read in from a 
    plain text file (one PMID per line)
'''

import argparse
import shutil
from pathlib import Path
from tqdm import tqdm

from preprocess.util import (ensure_path_exists,
                             file_exists_or_exit)

def get_pmid_set(args):

    ''' Return a set of PMIDs from args.pmid_file
        (items are strings, not ints)
    '''

    with open(args.pmid_file) as f:
        return set(line.rstrip('\n') for line in f.readlines())

def main(args):

    file_exists_or_exit(args.medline_paragraph_path)
    file_exists_or_exit(args.pmid_file)
    ensure_path_exists(args.output_directory)

    pmids_of_interest = get_pmid_set(args)
    print('Reading input files...')
    all_files = (f for f in Path(args.medline_paragraph_path).glob('**/*') if f.is_file())

    found_count = 0
    for medline_file in tqdm(all_files):
        if medline_file.name in pmids_of_interest:
            if found_count % 1000 == 0:
                current_subdir = '{0:0>4}'.format(found_count)
                ensure_path_exists(str(Path(args.output_directory) / current_subdir))
            found_count += 1
            new_file_path = str(Path(args.output_directory) / current_subdir / medline_file.name)
            shutil.copyfile(str(medline_file), new_file_path)

    print('Copied {} files (by PMID) to directory {}'.format(found_count, args.output_directory))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates a subset of MEDLINE based on a list of PMIDs')
    parser.add_argument('pmid_file', help='File of PMIDs to match')
    parser.add_argument('medline_paragraph_path', help='Directory of parsed MEDLINE paragraph files')
    parser.add_argument('output_directory', help='Final output directory')
    args = parser.parse_args()
    main(args)