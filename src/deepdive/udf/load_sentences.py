#!/usr/bin/env python3

import glob
import itertools
import os
os.chdir('/home/ubuntu/sandip/bioshovel_dd/src/deepdive')
import sys
import tarfile
import tempfile
from corenlp_parse import NLPParser
from util import (filter_files_from_tar,
                  load_config,
                  printl)

def parse_corenlp_output(filepath, pubtator_file_path):

    nlp_parser = NLPParser(filepath, pubtator_file_path)
    for i, row in enumerate(nlp_parser):
        print(row, flush=True)

    return None

def main(conf, current_chunk, total_chunks):
    # doc_id         text,
    # sentence_index int,
    # sentence_text  text,
    # tokens         text[],
    # lemmas         text[],
    # pos_tags       text[],
    # ner_tags       text[],
    # doc_offsets    int[],
    # dep_types      text[],
    # dep_tokens     int[]
    printl('Loading sentence data, Chunk {} of {}'.format(current_chunk,
                                                          total_chunks))

    if conf['data_tgz']:
        article_list = glob.glob(os.path.join(conf['data_directory'], '*.tgz'))
    article_chunk = [a for a in article_list if a.endswith('_{}_combined.tgz'.format(current_chunk))]
    if len(article_chunk) < 1:
        printl('Sentence loader - Chunk {} - no file found'.format(current_chunk))
        sys.exit(1)
    elif len(article_chunk) > 1:
        printl('Sentence loader - Chunk {} - multiple files found: {} (importing anyway)'.format(current_chunk,
                                                                                                 str(article_chunk)))

    for article_archive in article_chunk:
        printl(article_archive)
        with tarfile.open(article_archive, "r:gz") as tar, tempfile.TemporaryDirectory() as td:
            
            # corenlp output:
            output_files = filter_files_from_tar(tar, 'output_files')

            # pubtator output:
            pubtator_files = filter_files_from_tar(tar, 'pubtator')

            # extract pubtator and corenlp output files into tempdir
            tar.extractall(path=td, members=itertools.chain(output_files, pubtator_files))

            # glob/read through output_files and print file data
            output_filepaths = sorted(glob.glob(os.path.join(td,
                                                             '*',
                                                             'output_files',
                                                             '*')))
            pubtator_filepaths = sorted(glob.glob(os.path.join(td,
                                                               '*',
                                                               'pubtator',
                                                               '*')))

            for i, (fp, pubtator_fp) in enumerate(zip(output_filepaths, pubtator_filepaths)):
                parse_corenlp_output(fp, pubtator_fp)
                if i % 1000 == 0:
                    printl('Processed file {} of chunk'.format(i))

if __name__ == '__main__':
    conf = load_config()
    _, current_chunk, total_chunks = sys.argv
    main(conf, int(current_chunk), int(total_chunks))
