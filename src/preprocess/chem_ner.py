#!/usr/bin/env python3
'''chem_ner.py

requires Perl to be available in $PATH

usage:
cd bioshovel/src # this is the parent directory of this script file
python3 -m preprocess.chem_ner [path_to_paragraph_documents] [output_directory] --tmchem [path/to/tmChem.pl] --logdir [path/to/save/logfile]

runs:
perl tmChem.pl -i inputdir -o outputdir -m Model/All.Model
'''

import argparse
import logging
import logging.handlers
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from glob import glob, iglob
from itertools import repeat
import multiprocessing as mp
from pathlib import Path
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
        and calls tmChem using subprocess
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

    file_exists_or_exit(os.path.join(args.tmchem,'tmChem.pl'))

    args.paragraph_path = os.path.abspath(args.paragraph_path)

    # glob.glob doesn't support double star expressions in Python 3.4, so using this:
    print('Reading input files...')
    all_files = [str(f) for f in tqdm(Path(args.paragraph_path).glob('**/*')) if f.is_file()]

    filelist_with_sublists = create_n_sublists(all_files, mp.cpu_count()*1000)

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

    max_files_per_directory = 10000
    if len(all_files) > max_files_per_directory:
        print('Reorganizing output files into batches of {}...'.format(max_files_per_directory))
        for file_num, file_path in enumerate(tqdm(iglob(os.path.join(args.output_directory, '*')), total=len(all_files))):
            if file_num % max_files_per_directory == 0:
                # every n files, create new subdirectory and update current_subdir
                subdir_name = '{0:0>4}'.format(file_num//max_files_per_directory)
                path = Path(file_path)
                new_dir = path.parent / subdir_name
                new_dir.mkdir()
                current_subdir = str(new_dir)
            shutil.move(file_path, current_subdir)
        logging.info('Done reorganizing files into subdirectories')
    
    # end logging_thread
    q.put(None)
    log_thread.join()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run tmChem on a directory of paragraph files')
    parser.add_argument('paragraph_path', help='Directory of parsed paragraph files')
    parser.add_argument('output_directory', help='Final output directory')
    parser.add_argument('--tmchem', help='Directory where tmChem.pl is located', default=os.getcwd())
    parser.add_argument('--logdir', help='Directory where logfile should be stored', default='../logs')
    args = parser.parse_args()
    main(args)