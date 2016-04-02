#!/usr/bin/env python3
''' chem_ner_cluster.py

    for running preprocess.chem_ner on a PBS cluster (tested on TSRI Garibaldi cluster)
'''

import argparse
import os
import subprocess
import textwrap
from pathlib import Path
from tqdm import tqdm

from preprocess.util import (create_n_sublists,
                             ensure_path_exists,
                             file_exists_or_exit)

from preprocess.cluster.util import submit_pbs_job

def create_job_file(job_dir, sublist_dir, output_directory, chunk_num, args):

    ''' Create PBS job file in job_dir
    '''

    job_log_directory = os.path.join(args.logdir, 'sublist_{}'.format(chunk_num))
    ensure_path_exists(job_log_directory)
    cust_dict = {'output_dir': os.path.join(output_directory, 'chunk_{}'.format(chunk_num)),
                 'chunk_num': chunk_num,
                 'bioshovel_dir': args.bioshovel,
                 'tmchem': args.tmchem,
                 'input_paragraph_path': sublist_dir,
                 'job_log_directory': job_log_directory,
                 'poolsize': args.poolsize,
                 'walltime_hours': 240,
                 'cputime_hours': args.poolsize*240
                 }

    pbs_jobfile = textwrap.dedent('''
        #!/bin/bash
        #PBS -l nodes=1:ppn={poolsize}
        #PBS -l cput=960:00:00
        #PBS -l walltime={walltime_hours}:00:00
        #PBS -j oe
        #PBS -l mem=60gb
        #PBS -N "tmchem_{chunk_num}"
        #PBS -o tmchem_chunk{chunk_num}.out
        #PBS -m n

        # python 3.4+ required
        module load python/3.5.1

        # move to bioshovel directory and activate venv
        cd {bioshovel_dir}
        source venv/bin/activate

        # run preprocess.chem_ner
        cd src
        python3 -m preprocess.chem_ner {input_paragraph_path} {output_dir} --tmchem {tmchem} --logdir {job_log_directory} --notqdm --poolsize {poolsize}

        STATUS=$?
        if [ $STATUS -ne 0 ]; then
          echo "CoreNLP failed"; exit $STATUS
        else
          echo "Finished successfully!"
        fi
        ''').strip('\n').format(**cust_dict)

    job_file_path = os.path.join(job_dir, 'chem_ner_chunk{}.job'.format(chunk_num))
    with open(job_file_path, 'w') as f:
        f.write(pbs_jobfile)

    return job_file_path

def create_sublist_symlinks(sublist, input_dir, max_files):

    ''' Given an input directory input_dir and a list of absolute file paths 
        sublist, create symlinks for all files in sublist in input_dir, with no
        more than max_files files per subdirectory of input_dir
    '''

    for file_num, file_path in enumerate(sublist):
        if file_num % max_files == 0:
            subdir_name = '{0:0>4}'.format(file_num//max_files)
            current_subdir = os.path.join(input_dir, subdir_name)
            ensure_path_exists(current_subdir)

        subprocess.check_call(['ln', '-s', file_path, '.'], cwd=current_subdir)

def main(args):

    # make all paths absolute (to simplify things later)
    args.paragraph_path = os.path.abspath(args.paragraph_path)
    args.output_directory = os.path.abspath(args.output_directory)
    args.logdir = os.path.abspath(args.logdir)
    args.tmchem = os.path.abspath(args.tmchem)
    args.bioshovel = os.path.abspath(args.bioshovel)

    file_exists_or_exit(os.path.join(args.tmchem,'tmChem.pl'))

    # get all files (recursive)
    print('Reading input files...')
    all_files = [str(f) for f in tqdm(Path(args.paragraph_path).glob('**/*')) if f.is_file()]

    # divide list into n chunks (number of jobs to create)
    print('Splitting input file list into batches...')
    filelist_with_sublists = create_n_sublists(all_files, args.njobs)

    # move job files into the appropriate subdirectories
    # (don't store more than 1k per sub-subdirectory)
    # create job file for each subdirectory

    print('Organizing input files and creating job files...')
    base_input_directory = os.path.join(args.output_directory, 'input_files')
    job_dir = os.path.join(args.output_directory, 'job_files')
    output_directory = os.path.join(args.output_directory, 'output')
    for path in (base_input_directory, job_dir, output_directory):
        ensure_path_exists(path)
    job_file_paths = []
    for sublist_num, sublist in enumerate(tqdm(filelist_with_sublists)):
        sublist_dir = os.path.join(base_input_directory, 
                                   'sublist_{0:0>4}'.format(sublist_num))
        ensure_path_exists(sublist_dir)
        create_sublist_symlinks(sublist, sublist_dir, 1000)
        job_file_path = create_job_file(job_dir, sublist_dir, output_directory, sublist_num, args)
        job_file_paths.append(job_file_path)

    # submit jobs to queue ('new')
    if args.submit:
        print('Submitting {} jobs...'.format(len(job_file_paths)))
        for job_file_path in tqdm(job_file_paths):
            result = submit_pbs_job(job_file_path, queue=args.queue)
            if not result:
                print('Job submission failed: {}'.format(job_file_path))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run preprocess.chem_ner as a collection of cluster jobs')
    parser.add_argument('paragraph_path',
                        help='Directory of parsed paragraph files')
    parser.add_argument('output_directory',
                        help='Final output directory')
    parser.add_argument('--tmchem',
                        help='Directory where tmChem.pl is located',
                        default=os.getcwd())
    parser.add_argument('--logdir',
                        help='Directory where logfile should be stored',
                        default='../logs')
    parser.add_argument('--bioshovel',
                        help='Path to bioshovel directory',
                        default='/gpfs/group/su/sandip/bioshovel')
    parser.add_argument('--queue',
                        help='Cluster queue for job submission',
                        default='new')
    parser.add_argument('--submit',
                        help='Submit jobs after creating job files',
                        action='store_true')
    parser.add_argument('--njobs',
                        help='Number of PBS jobs to create',
                        default=500)
    parser.add_argument('--poolsize',
                        help='Size of multiprocessing process pool',
                        type=int,
                        default=8)
    args = parser.parse_args()
    main(args)