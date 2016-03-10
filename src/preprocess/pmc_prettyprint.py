#!/usr/bin/env python3

# usage:
# python3 pmc_prettyprint.py [root_directory]

# Create a pretty-printed version
# of the PubMed Central XML corpus
#
# New files will be created with same 
# directory structure in pretty_[root_directory]

import os
import sys
from bs4 import BeautifulSoup

def prettify(input_xml_string):

    ''' returns prettified xml string
        (with newlines and indentation)
    '''

    soup = BeautifulSoup(input_xml_string, 'html.parser')
    return soup.prettify()

def write_prettified_sibling(input_file, output_file):

    ''' reads input_file and writes
        prettify(input_file) to output_file
    '''

    with open(input_file) as i, open(output_file, 'w') as o:
        o.write(prettify(i.read()))

def main():
    
    assert len(sys.argv) == 2, 'wrong number of arguments'
    top_dir = sys.argv[1]
    prettified_directory_prefix = 'pretty_'

    for root, dirs, files in os.walk(top_dir):
        print('Reading directory {}'.format(root))

        if any(filename for filename in files if filename.endswith('.nxml')):
            new_root = prettified_directory_prefix+root

            # check if directory exists and create if necessary
            if not os.path.isdir(new_root):
                os.makedirs(new_root)

            for filename in files:
                write_prettified_sibling(os.path.join(root,filename), os.path.join(new_root,filename))

if __name__ == '__main__':
    main()