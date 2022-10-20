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

def parse_corenlp_output(conf, filepath, pubtator_file_path):

    if conf['fuzzy_ner_match']:
        fuzzy_ratio = conf['fuzzy_ratio']
    else:
        fuzzy_ratio = False

    nlp_parser = NLPParser(filepath,
                           pubtator_file_path,
                           fuzzy_ner_match=fuzzy_ratio)
    if pubtator_file_path:
        if not nlp_parser.update_ner_pubtator():
            printl('Unable to update generic NER with PubTator matches')
    for row in nlp_parser.get_biothing_tokens():
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

            if conf['parse_pubtator']:
                # pubtator output:
                pubtator_files = filter_files_from_tar(tar, 'pubtator')
            else:
                pubtator_files = []

            # extract pubtator and corenlp output files into tempdir
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, path=td, members=itertools.chain(output_files,pubtator_files))

            # glob/read through output_files and print file data
            output_filepaths = sorted(glob.glob(os.path.join(td,
                                                             '*',
                                                             'output_files',
                                                             '*')))
            if conf['parse_pubtator']:
                pubtator_filepaths = sorted(glob.glob(os.path.join(td,
                                                                   '*',
                                                                   'pubtator',
                                                                   '*')))
            else:
                # pubtator_filepaths = [None for _ in output_filepaths]
                sys.exit(1)

            for i, (fp, pubtator_fp) in enumerate(zip(output_filepaths, pubtator_filepaths)):
                parse_corenlp_output(conf, fp, pubtator_fp)
                if i % 1000 == 0:
                    printl('Processed file {} of chunk'.format(i))

if __name__ == '__main__':
    conf = load_config()
    _, current_chunk, total_chunks = sys.argv
    main(conf, int(current_chunk), int(total_chunks))
