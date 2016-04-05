#!/usr/bin/env python3
'''disease_ner.py

For performing disease name-entity recognition on paragraph data in parform format

requires `java` to be available in $PATH

usage:
cd bioshovel/src # this is the parent directory of this script file
python3 -m preprocess.disease_ner [path_to_paragraph_documents] [output_directory] --dnorm [absolute/path/to/dnorm/ApplyDNorm.sh/directory] --logdir [path/to/save/logfile]

runs:
./ApplyDNorm.sh config/banner_NCBIDisease_UMLS2013AA_TEST.xml data/CTD_diseases.tsv output/simmatrix_NCBIDisease_e4.bin [absolute/path/to/Ab3P-v1.5/directory] temp_directory input_file.txt output_file.txt

(runs each file individually because DNorm doesn't appear to work with an input directory...)
'''

import argparse
import logging
import logging.handlers
import os
import psutil
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
                             file_exists_or_exit,
                             reorganize_directory)
from preprocess.reformat import (parse_parform_file, 
                                 parform_to_pubtator)

def process_and_run_chunk(filepaths_args_tuple):

    ''' Generates reformatted files for each file path in 
        list_of_file_paths, saves them to a single temp directory,
        and calls DNorm on each individual file using subprocess
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

    reqs = {'banner_ncbidisease': os.path.join(args.dnorm,
                                               'config', 
                                               'banner_NCBIDisease_UMLS2013AA_TEST.xml'),
            'ctd_diseases': os.path.join(args.dnorm,
                                         'data',
                                         'CTD_diseases.tsv'),
            'simmatrix': os.path.join(args.dnorm,
                                      'output',
                                      'simmatrix_NCBIDisease_e4.bin'),
            'ab3p_path': os.path.join(args.dnorm,
                                      '..',
                                      'Ab3P-v1.5')}
    for required_file in reqs:
        file_exists_or_exit(reqs[required_file])

    with tempfile.TemporaryDirectory() as input_tempdir, tempfile.TemporaryDirectory() as output_tempdir, tempfile.TemporaryDirectory() as dnorm_tempdir:
        for doi_filename, file_info in reformatted_files:
            save_file(doi_filename, file_info, input_tempdir)

            try:
                out = subprocess.check_output(['bash',
                                               'ApplyDNorm.sh',
                                               reqs['banner_ncbidisease'],
                                               reqs['ctd_diseases'],
                                               reqs['simmatrix'],
                                               reqs['ab3p_path'],
                                               dnorm_tempdir,
                                               os.path.join(input_tempdir,
                                                            doi_filename),
                                               os.path.join(output_tempdir,
                                                            doi_filename)],
                                               cwd=args.dnorm,
                                               stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as err:
                string_error = err.output.decode(encoding='UTF-8').rstrip('\n')
                l.critical('DNorm error: {}'.format(string_error))
                l.critical('DNorm error while processing chunk: {}'.format(list_of_file_paths))

        # grab all new output files and copy to args.output_directory
        all_tempfiles = glob(os.path.join(output_tempdir, '*'))

        try:
            subprocess.check_output(['cp', '-t', args.output_directory+'/'] + all_tempfiles)
        except subprocess.CalledProcessError:
            l.critical('Copy error, chunk: {}'.format(list_of_file_paths))

def main(args):
    
    file_exists_or_exit(os.path.join(args.dnorm, 'ApplyDNorm.sh'))

    all_files = glob(os.path.join(args.paragraph_path, '*'))
    filelist_with_sublists = create_n_sublists(all_files, mp.cpu_count()*10)

    # check if save_directory exists and create if necessary
    if not os.path.isdir(args.output_directory):
        os.makedirs(args.output_directory)

    log_filename = os.path.join(args.logdir, 'disease_ner.log')
    logging_format = '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
    logging.basicConfig(filename=log_filename,
                        format=logging_format,
                        level=logging.INFO,
                        filemode='w')

    # each java process requires 10G of RAM. How many can we start?
    ram_gb = psutil.virtual_memory().total//1024**3
    num_java_processes = ram_gb//10

    # don't start more processes than CPU cores (or cores allocated for job)
    num_java_processes = min(num_java_processes, args.poolsize)

    print('Using {} cores to process {} files...'.format(num_java_processes, 
                                                         len(all_files)))
    print('Using {} GB of {} GB total RAM'.format(num_java_processes*10,
                                                  ram_gb))

    with mp.Pool(num_java_processes) as pool:
        mgr = mp.Manager()
        q = mgr.Queue()
        log_thread = threading.Thread(target=logging_thread, args=(q,))
        log_thread.start()
        imap_gen = pool.imap_unordered(process_and_run_chunk, 
                                       zip(filelist_with_sublists, 
                                           repeat(args),
                                           repeat(q)))
        for i in tqdm(imap_gen,
                      total=len(filelist_with_sublists),
                      disable=args.notqdm):
            pass

    logging.info('Done processing {} files'.format(len(all_files)))

    # reorganize a directory with a huge number of files into a bunch of
    # subdirectories containing those same files, with a max of 10k files per
    # subdirectory
    reorganize_directory(args.output_directory,
                         max_files_per_subdir=10000,
                         quiet=args.notqdm)
    
    # end logging_thread
    q.put(None)
    log_thread.join()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run DNorm on a directory of paragraph files')
    parser.add_argument('paragraph_path',
                        help='Directory of parsed paragraph files')
    parser.add_argument('output_directory',
                        help='Final output directory')
    parser.add_argument('--dnorm',
                        help='Directory (absolute path) where ApplyDNorm.sh is located',
                        default=os.getcwd())
    parser.add_argument('--logdir',
                        help='Directory where logfile should be stored',
                        default='../logs')
    parser.add_argument('--poolsize',
                        help='Size of multiprocessing process pool',
                        type=int,
                        default=mp.cpu_count())
    parser.add_argument('--notqdm', help='Disable tqdm progress bar output',
                        action='store_true')
    args = parser.parse_args()
    main(args)