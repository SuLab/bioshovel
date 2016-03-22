#!/usr/bin/env python3
'''gene_ner.py

For performing gene name-entity recognition on paragraph data in parform format

requires Perl to be available in $PATH

usage:
cd bioshovel/src # this is the parent directory of this script file
python3 -m preprocess.gene_ner [path_to_paragraph_documents] [output_directory] --gnormplus [absolute/path/to/GNormPlus.pl] --logdir [path/to/save/logfile]

runs:
perl GNormPlus.pl -i inputdir -o outputdir -s setup.txt
'''

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

from preprocess.util import (save_file,
                             create_n_sublists,
                             logging_thread,
                             file_exists_or_exit)
from preprocess.reformat import (parse_parform_file, 
                                 parform_to_pubtator)

def process_and_run_chunk(filepaths_args_tuple):

    ''' Generates reformatted files for each file path in 
        list_of_file_paths, saves them to a single temp directory,
        and calls GNormPlus using subprocess
    '''

    list_of_file_paths, args, q = filepaths_args_tuple

    if not list_of_file_paths:
        return

    qh = logging.handlers.QueueHandler(q)
    l = logging.getLogger()

    parsed_files = [parse_parform_file(file_path)
                    for file_path in list_of_file_paths]

    # filter out files with no title line 
    # (for which parse_parform_file returned None)
    parsed_files = [f for f in parsed_files if f]

    reformatted_files = [parform_to_pubtator(escaped_doi, title_line, body)
                         for escaped_doi, title_line, body in parsed_files]

    with tempfile.TemporaryDirectory() as input_tempdir, tempfile.TemporaryDirectory() as output_tempdir:
        for doi_filename, file_info in reformatted_files:
            save_file(doi_filename, file_info, input_tempdir)

        try:
            out = subprocess.check_output(['perl', 
                                          os.path.join(args.gnormplus, 
                                                       'GNormPlus.pl'), 
                                          '-i', input_tempdir,
                                          '-o', output_tempdir,
                                          '-s', os.path.join(args.gnormplus, 
                                                             'setup.txt')
                                          ],
                                          cwd=args.gnormplus,
                                          stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            string_error = err.output.decode(encoding='UTF-8').rstrip('\n')
            l.critical('GNormPlus error: {}'.format(string_error))
            l.critical('GNormPlus error while processing chunk: {}'.format(list_of_file_paths))

        all_tempfiles = glob(os.path.join(output_tempdir, '*'))

        try:
            subprocess.check_output(['cp', '-t', args.output_directory+'/'] + all_tempfiles)
        except subprocess.CalledProcessError:
            l.critical('Copy error, chunk: {}'.format(list_of_file_paths))

def main(args):
    
    file_exists_or_exit(os.path.join(args.gnormplus, 'GNormPlus.pl'))

    all_files = glob(os.path.join(args.paragraph_path, '*'))
    filelist_with_sublists = create_n_sublists(all_files, mp.cpu_count()*10)

    # check if save_directory exists and create if necessary
    if not os.path.isdir(args.output_directory):
        os.makedirs(args.output_directory)

    log_filename = os.path.join(args.logdir, 'gene_ner.log')
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

    parser = argparse.ArgumentParser(description='Run GNormPlus on a directory of paragraph files')
    parser.add_argument('paragraph_path', help='Directory of parsed paragraph files')
    parser.add_argument('output_directory', help='Final output directory')
    parser.add_argument('--gnormplus', help='Directory (absolute path) where GNormPlus.pl is located', default=os.getcwd())
    parser.add_argument('--logdir', help='Directory where logfile should be stored', default='../logs')
    args = parser.parse_args()
    main(args)