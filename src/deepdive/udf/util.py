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
