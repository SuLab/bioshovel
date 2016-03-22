#!/usr/bin/env python3

# Helper functions for preprocess module

import logging
import os
import sys

def save_file(file_name, file_info, directory):

    ''' Saves file specified by file_info (a list of file lines, 
        including newlines) to a new tempfile in directory
    '''

    with open(os.path.join(directory, file_name), 'w') as f:
        for line in file_info:
            f.write(line)

def create_n_sublists(full_list, n=10):

    ''' Returns a list of n sublists generated from full_list using stride of n
    '''

    return [full_list[i::n] for i in range(n)]

def logging_thread(q):

    ''' Handles logging to logfile while other processes are running

        (exits upon receiving None in queue)
    '''

    while True:
        record = q.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)

def file_exists_or_exit(file_path):

    ''' Exit if the file at specified by file_path doesn't exist
    '''

    if not os.path.exists(file_path):
        print('File does not exist: {}'.format(file_path), file=sys.stderr)
        sys.exit(1)