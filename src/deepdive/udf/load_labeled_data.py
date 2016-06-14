#!/usr/bin/env python3

import glob
import itertools
import os
os.chdir(os.environ['CURRENT_DD_APP'])
import sys
import tarfile
import tempfile
from corenlp_parse import NLPParser
from util import (filter_files_from_tar,
                  load_config,
                  printl)

def parse_corenlp_output_for_cid(conf, filepath, pubtator_file_path):

    if conf['fuzzy_ner_match']:
        fuzzy_ratio = conf['fuzzy_ratio']
    else:
        fuzzy_ratio = False

    nlp_parser = NLPParser(filepath,
                           pubtator_file_path,
                           fuzzy_ner_match=fuzzy_ratio)

    # need to get sentence lines containing CID relations for this document...
    for sentences_row in nlp_parser.get_cid_filtered_sentence_rows():
        print(sentences_row, flush=True)

    return None

def main(conf):

    printl('Loading training data...')

    if conf['data_tgz']:
        article_list = glob.glob(os.path.join(conf['training_data_directory'], '*.tgz'))
    article_chunk = [a for a in article_list if a.endswith('_combined.tgz')]

    for article_archive in article_chunk:
        printl(article_archive)
        with tarfile.open(article_archive, "r:gz") as tar, tempfile.TemporaryDirectory() as td:
            
            # corenlp output:
            output_files = filter_files_from_tar(tar, 'output_files')

            if conf['parse_pubtator']:
                # pubtator_cid output:
                pubtator_files = filter_files_from_tar(tar, 'pubtator_cid')
            else:
                pubtator_files = []

            # extract pubtator and corenlp output files into tempdir
            tar.extractall(path=td, members=itertools.chain(output_files, pubtator_files))

            # glob/read through output_files and print file data
            output_filepaths = sorted(glob.glob(os.path.join(td,
                                                             '*',
                                                             'output_files',
                                                             '*')))
            if conf['parse_pubtator']:
                pubtator_filepaths = sorted(glob.glob(os.path.join(td,
                                                                   '*',
                                                                   'pubtator_cid',
                                                                   '*')))
            else:
                printl('Need to parse PubTator files for CID relations-- check config file')
                sys.exit(1)

            for i, (fp, pubtator_fp) in enumerate(zip(output_filepaths, pubtator_filepaths)):
                parse_corenlp_output_for_cid(conf, fp, pubtator_fp)
                if i % 1000 == 0:
                    printl('Processed file {} of chunk'.format(i))

if __name__ == '__main__':
    conf = load_config()
    main(conf)