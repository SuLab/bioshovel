#!/usr/bin/env python3

import json
import sys

def load_config(filename='bioshovel_config.json'):

    ''' Loads a JSON-formatted config file and returns a dictionary object
    '''

    with open(filename) as f:
        return json.load(f)

def printl(string):

    ''' Prints string to STDERR and flushes buffer

        (used to print output to DeepDive logfile instead of to 
         STDOUT/DD application pipeline)
    '''

    print('BIOSHOVEL', string, file=sys.stderr, flush=True)

def filter_files_from_tar(tarfile_obj, filter_string):

    ''' Given a TarFile object, return all files containing filter_string in
        their path -- return files from the archive as generator of TarInfo
        objects
    '''

    for tfmem in tarfile_obj.getmembers():
        if tfmem.isfile() and filter_string in tfmem.name:
            yield tfmem
