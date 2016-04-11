#!/usr/bin/env python3

# Helper functions for preprocess module

import itertools
import logging
import multiprocessing as mp
import os
import psutil
import shutil
import subprocess
import sys
from glob import iglob
from pathlib import Path
from tqdm import tqdm

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

def reorganize_directory(file_path, max_files_per_subdir=1000, quiet=True):

    ''' Reorganize a single directory with no subdirectories and a large number
        of files into a number of subdirectories containing those files, with
        no more than max_files_per_subdir files per subdirectory
    '''

    # count files using generator and sum in case the directory has a massive
    # number of files...
    total_files_in_dir = sum(1 for file_path in iglob(os.path.join(file_path,'*')))

    if total_files_in_dir > max_files_per_subdir:
        if not quiet:
            print('Reorganizing output files into batches of {}...'.format(max_files_per_subdir))
        for file_num, file_path in enumerate(tqdm(iglob(os.path.join(file_path,'*')),
                                                  total=total_files_in_dir,
                                                  disable=quiet)):
            if file_num % max_files_per_subdir == 0:
                # every n files, create new subdirectory and update current_subdir
                subdir_name = '{0:0>4}'.format(file_num//max_files_per_subdir)
                path = Path(file_path)
                new_dir = path.parent / subdir_name
                new_dir.mkdir()
                current_subdir = str(new_dir)
            shutil.move(file_path, current_subdir)
        if not quiet:
            print('Done reorganizing files into subdirectories')

def create_sublist_symlinks(sublist, input_dir, max_files=1000):

    ''' Given an input directory input_dir and a list of absolute file paths 
        sublist, create symlinks for all files in sublist in input_dir, with no
        more than max_files files per subdirectory of input_dir
    '''

    for file_num, file_path in enumerate(sublist):
        if not file_path:
            continue
        if file_num % max_files == 0:
            subdir_name = '{0:0>4}'.format(file_num//max_files)
            current_subdir = os.path.join(input_dir, subdir_name)
            ensure_path_exists(current_subdir)

        subprocess.check_call(['ln', '-s', file_path, '.'], cwd=current_subdir)

def calc_dnorm_num_processes(num_cores=mp.cpu_count(), ram_gb=None):

    ''' Each DNorm (Disease NER) Java process requires 10GB of RAM

        How many can we start, given the number of cores and amount of RAM (in
        GB) available?
    '''

    if not ram_gb:
        ram_gb = psutil.virtual_memory().total//1024**3

    num_java_processes = ram_gb//10

    return min(num_java_processes, num_cores)

def get_file_lines_set(file_path_str, typecast=None):

    ''' Return a set consisting of the lines of an input file at file_path_str,
        with trailing newline characters stripped

        typecast argument can be int, str, float, etc.
    '''

    if not typecast:
        typecast = str

    with open(file_path_str) as f:
        return set(typecast(line.rstrip('\n')) for line in f.readlines())