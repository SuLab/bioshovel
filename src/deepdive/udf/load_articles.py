#!/usr/bin/env python3

import glob
import json
import os
os.chdir(os.environ['CURRENT_DD_APP'])
import sys
import tarfile
import tempfile
from pathlib import Path
from util import (filter_files_from_tar,
                  load_config,
                  printl)

def clean_string(contents, newline_replacement='//n'):

    ''' Replace tabs in contents with a single space
    '''

    return contents.replace('\t', ' ').replace('\n', newline_replacement)

def print_article_info(filepath, article_archive_path_str, train_dev_test_dict):

    ''' Given a filepath, print the file contents as a tab-delimited tuple:

        file_path_basename[tab]file_contents[tab]article_archive[tab]article_filepath[tab]corenlp_filepath[tab]pubtator_filepath

        where file_contents has all tabs replaced by spaces, and filepaths are relative

        This is for the 'articles' table schema:

        articles(
            doc_id              text,
            content             text,
            article_archive     text,
            article_filepath    text,
            corenlp_filepath    text,
            pubtator_filepath   text
        ).
    '''

    # filepath is something like:
    # Path('/tmp/tmpdirectory12345/tarfile_0_combined/input_files/928240')

    filepath_str = str(filepath)

    filename_stem = filepath.stem
    relative_input_filepath_str = str(Path(filepath.parent.stem)/filename_stem)
    relative_corenlp_filepath_str = str(Path('output_files')/(filename_stem+'.json'))
    relative_pubtator_filepath_str = str(Path('pubtator')/filename_stem)
    # test_set = 'test' if filename_stem in test_set_pmids else 'traindev'

    with open(filepath_str) as f:
        print(filename_stem,
              clean_string(f.read()),
              article_archive_path_str,
              relative_input_filepath_str,
              relative_corenlp_filepath_str,
              relative_pubtator_filepath_str,
              train_dev_test_dict.get(filename_stem, ''), # returns 'train', 'test', 'dev', or empty string
              sep='\t')

def main(conf, current_chunk, total_chunks):

    printl('Loading article data, Chunk {} of {}'.format(current_chunk,
                                                          total_chunks))

    if conf['data_tgz']:
        article_list = glob.glob(os.path.join(conf['data_directory'], '*.tgz'))
    else:
        raise NotImplementedError("Can't handle nongzipped files yet")
    article_chunk = [a for a in article_list if a.endswith('_{}_combined.tgz'.format(current_chunk))]
    if len(article_chunk) < 1:
        printl('Article loader - Chunk {} - no file found'.format(current_chunk))
        sys.exit(1)
    elif len(article_chunk) > 1:
        printl('Article loader - Chunk {} - multiple files found: {} (importing anyway)'.format(current_chunk,
                                                                                                str(article_chunk)))

    # with open('/home/ubuntu/sandip/bioshovel_biocreative_update/src/deepdive/test_set_pmids.txt') as f:
    #     test_set_pmids = set([line.rstrip('\n') for line in f.readlines()])

    with open(conf['train_dev_test_ids_json']) as f:
        train_dev_test_dict = json.load(f)

    for article_archive in article_chunk:
        printl(article_archive)
        with tarfile.open(article_archive, "r:gz") as tar, tempfile.TemporaryDirectory() as td:
            input_files = filter_files_from_tar(tar, 'input_files')

            # extract input_files into tempdir
            tar.extractall(path=td, members=input_files)

            # glob/read through input_files and print file data
            input_filepaths = glob.glob(os.path.join(td,
                                                     '*',
                                                     'input_files',
                                                     '*'))

            for i, filepath in enumerate(input_filepaths):
                print_article_info(Path(filepath), article_archive, train_dev_test_dict)
                if i % 500 == 0:
                    printl('Processed file {} of chunk'.format(i))

if __name__ == '__main__':
    conf = load_config()
    _, current_chunk, total_chunks = sys.argv
    main(conf, int(current_chunk), int(total_chunks))
