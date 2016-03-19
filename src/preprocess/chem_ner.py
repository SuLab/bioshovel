#!/usr/bin/env python3

# chem_ner.py

# requires Perl to be available in $PATH

# usage:
# python3 chem_ner.py [path_to_paragraph_documents] [output_directory] --tmchem [path/to/tmChem.pl] --logdir [path/to/save/logfile]

# runs:
# perl tmChem.pl -i inputdir -o outputdir -m Model/All.Model

import argparse
import logging
import logging.handlers
import os
import subprocess
import sys
import tempfile
import threading
from glob import glob
from itertools import repeat
import multiprocessing as mp
from tqdm import tqdm

from .util import (save_file,
                  create_n_sublists,
                  logging_thread)

def reformat_parsed_article(parsed_article_path):

    ''' Read in file parsed_article_path with format:
        title\tsome_title_text
        [abs\t]some_abstract_text
        p\tparagraph1_text
        p\tparagraph2_text
        ...

        Output:
        List of new file lines (including newlines) with format:
        [escaped DOI]_a|article_title
        [escaped_DOI]_a|article_abstract

        [escaped DOI]_1|article_title
        [escaped_DOI]_1|article_paragraph1

        [escaped DOI]_2|article_title
        [escaped_DOI]_2|article_paragraph2
    '''

    with open(parsed_article_path) as f:
        title_line = f.readline().rstrip('\n')
        if not title_line.startswith('title'):
            print('Not a title line...')
            return
        body = [line.rstrip('\n') for line in f.readlines()]

    article_title = title_line.split('\t')[1]
    escaped_doi = os.path.basename(parsed_article_path)

    new_file_lines = []
    new_title_line = escaped_doi+'_{}|t|'+article_title

    # if there is an abstract line, treat it separately
    if body[0].startswith('abs\t'):
        abstract = body[0].split('\t')[1]
        new_file_lines.append(new_title_line.format('a'))
        new_file_lines.append(escaped_doi+'_a|a|'+abstract)
        new_file_lines.append('')
        body = body[1:]

    for line_num, line in enumerate(body):
        new_file_lines.append(new_title_line.format(line_num+1))

        # allows for tabs in the paragraph content...
        paragraph_content = '\t'.join(line.split('\t')[1:])
        new_file_lines.append(escaped_doi+
                              '_{}|a|'.format(line_num+1)+
                              paragraph_content)
        new_file_lines.append('')

    return (escaped_doi, [line+'\n' for line in new_file_lines])

def process_and_run_chunk(filepaths_args_tuple):

    ''' Generates reformatted files for each file path in 
        list_of_file_paths, saves them to a single temp directory,
        and calls tmChem using subprocess
    '''

    list_of_file_paths, args, q = filepaths_args_tuple

    if not list_of_file_paths:
        return

    qh = logging.handlers.QueueHandler(q)
    l = logging.getLogger()

    reformatted_files = [reformat_parsed_article(file_path) 
                         for file_path in list_of_file_paths]

    with tempfile.TemporaryDirectory() as input_tempdir, tempfile.TemporaryDirectory() as output_tempdir:
        for doi_filename, file_info in reformatted_files:
            save_file(doi_filename, file_info, input_tempdir)

        try:
            out = subprocess.check_output(['perl', 
                                          os.path.join(args.tmchem, 
                                                       'tmChem.pl'), 
                                          '-i', input_tempdir,
                                          '-o', output_tempdir,
                                          '-m', os.path.join(args.tmchem, 
                                                             'Model', 
                                                             'All.Model')
                                          ],
                                          cwd=args.tmchem,
                                          stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            string_error = err.output.decode(encoding='UTF-8').rstrip('\n')
            l.critical('tmChem error: {}'.format(string_error))
            l.critical('tmChem error while processing chunk: {}'.format(list_of_file_paths))

        all_tempfiles = glob(os.path.join(output_tempdir, '*'))

        try:
            subprocess.check_output(['cp', '-t', args.output_directory+'/'] + all_tempfiles)
        except subprocess.CalledProcessError:
            l.critical('Copy error, chunk: {}'.format(list_of_file_paths))

def main(args):

    # check to make sure tmChem.pl exists
    if not os.path.exists(os.path.join(args.tmchem,'tmChem.pl')):
        print('tmChem.pl does not exist in path: {}'.format(args.tmchem))
        sys.exit(1)

    all_files = glob(os.path.join(args.paragraph_path, '*'))
    filelist_with_sublists = create_n_sublists(all_files, mp.cpu_count()*10)

    # check if save_directory exists and create if necessary
    if not os.path.isdir(args.output_directory):
        os.makedirs(args.output_directory)

    log_filename = os.path.join(args.logdir, 'chem_ner.log')
    logging_format = '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
    logging.basicConfig(filename=log_filename,
                        format=logging_format,
                        level=logging.INFO,
                        filemode='w')

    print('Using {} cores to process {} files...'.format(mp.cpu_count(), 
                                                         len(all_files)))

    with mp.Pool() as pool:
        mgr = mp.Manager()
        q = mgr.Queue()
        log_thread = threading.Thread(target=logging_thread, args=(q,))
        log_thread.start()
        imap_gen = pool.imap_unordered(process_and_run_chunk, 
                                        zip(filelist_with_sublists, 
                                            repeat(args),
                                            repeat(q)))
        for i in tqdm(imap_gen, total=len(filelist_with_sublists)):
            pass

    logging.info('Done processing {} files'.format(len(all_files)))
    
    # end logging_thread
    q.put(None)
    log_thread.join()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run tmChem on a directory of paragraph files')
    parser.add_argument('paragraph_path', help='Directory of parsed paragraph files')
    parser.add_argument('output_directory', help='Final output directory')
    parser.add_argument('--tmchem', help='Directory where tmChem.pl is located', default=os.getcwd())
    parser.add_argument('--logdir', help='Directory where logfile should be stored', default='../../logs')
    args = parser.parse_args()
    main(args)