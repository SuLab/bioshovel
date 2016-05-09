#!/usr/bin/env python3

import glob
import json
import os
import sys
import tarfile
import tempfile
from udf import util

def clean_string(contents, newline_replacement='//n'):

    ''' Replace tabs in contents with a single space
    '''

    return contents.replace('\t', ' ').replace('\n', newline_replacement)

def print_article_info(filepath):

    ''' Given a filepath, print the file contents as a tab-delimited tuple:

        file_path_basename[tab]file_contents

        where file_contents has all tabs replaced by spaces

        (this is for the 'articles' table schema: columns (doc_id, contents))
    '''

    with open(filepath) as f:
        print(os.path.basename(filepath), clean_string(f.read()), sep='\t')

def filter_files_from_tar(tarfile_obj, filter_string):

    ''' Given a TarFile object, return all files containing filter_string in
        their path -- return files from the archive as generator of TarInfo
        objects
    '''

    for tfmem in tarfile_obj.getmembers():
        if tfmem.isfile() and filter_string in tfmem.name:
            yield tfmem

def main(conf):

    if conf['data_tgz']:
        article_list = glob.glob(os.path.join(conf['data_directory'], '*.tgz'))
        util.printl('Reading through {} .tgz archive files...'.format(len(article_list)))
        for i, article_archive in enumerate(article_list):
            with tarfile.open(article_archive, "r:gz") as tar, tempfile.TemporaryDirectory() as td:
                input_files = filter_files_from_tar(tar, 'input_files')

                # extract input_files into tempdir
                tar.extractall(path=td, members=input_files)

                # glob/read through input_files and print file data
                input_filepaths = glob.glob(os.path.join(td,
                                                         '*',
                                                         'input_files',
                                                         '*'))

                for filepath in input_filepaths:
                    print_article_info(filepath)

                util.printl('Processed tgz archive #{} of {}'.format(i+1,
                                                                len(article_list)))

    else:
        raise NotImplementedError("Can't handle nongzipped files yet")

if __name__ == '__main__':
    conf = util.load_config()
    main(conf)
