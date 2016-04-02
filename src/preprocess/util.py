#!/usr/bin/env python3

# Helper functions for preprocess module

import itertools
import logging
import os
import subprocess
import sys

def save_file(file_name, file_info, directory):

    ''' Saves file specified by file_info (a list of file lines, 
        including newlines) to a new tempfile in directory

        Return path to new file
    '''

    new_file_path = os.path.join(directory, file_name)
    with open(new_file_path, 'w') as f:
        for line in file_info:
            f.write(line)

    return new_file_path

def create_n_sublists(full_list, n=10):

    ''' Returns a list of n sublists generated from full_list using stride of n
    '''

    return [full_list[i::n] for i in range(n)]

def create_sublists_sized_n(full_list, n=500):

    ''' Returns a list of sublists, each with length of n
        (some lists will contain None values as filler)
    '''

    args = [iter(full_list)] * n
    return itertools.zip_longest(*args)

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
        print('Required file does not exist: {}'.format(file_path), file=sys.stderr)
        sys.exit(1)

def shell_command_exists_or_exit(command):

    ''' Exit if command (string) does not exist in system $PATH

        (runs `which [command]` and checks for nonzero exit code)
    '''

    try:
        subprocess.check_call(['which']+command.split(' ')[:1],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print('Command `{}` does not exist in $PATH -- exiting'.format(command), 
              file=sys.stderr)
        sys.exit(1)

    return True

def ensure_path_exists(path):

    ''' check if directory exists. if not, create it.
    '''

    if not os.path.isdir(path):
        os.makedirs(path)