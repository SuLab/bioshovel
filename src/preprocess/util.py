#!/usr/bin/env python3

# Helper functions for preprocess module

import logging
import os

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