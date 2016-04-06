#!/usr/bin/env python3
''' disease_ner_cluster.py

    for running preprocess.disease_ner on a PBS cluster
    (tested on TSRI Garibaldi cluster)
'''

import argparse
import os
import subprocess
import textwrap
from pathlib import Path
from tqdm import tqdm

from preprocess.util import (create_sublists_sized_n,
                             create_sublist_symlinks,
                             ensure_path_exists,
                             file_exists_or_exit)

from preprocess.cluster.util import submit_pbs_job

def create_job_file(job_dir, sublist_dir, output_directory, chunk_num, args):

    ''' Create PBS job file for DNorm (preprocess.disease_ner) in job_dir
    '''

    job_log_directory = os.path.join(args.logdir, 'sublist_{}'.format(chunk_num))
    ensure_path_exists(job_log_directory)
    cust_dict = {'output_dir': os.path.join(output_directory, 'chunk_{}'.format(chunk_num)),
                 'chunk_num': chunk_num,
                 'bioshovel_dir': args.bioshovel,
                 'dnorm': args.dnorm,
                 'input_paragraph_path': sublist_dir,
                 'job_log_directory': job_log_directory,
                 'poolsize': args.poolsize,
                 'walltime_hours': 240,
                 'cputime_hours': args.poolsize*240,
                 'memgb': args.memgb
                 }

    pbs_jobfile = textwrap.dedent('''
        #!/bin/bash
        #PBS -l nodes=1:ppn={poolsize}
        #PBS -l cput=960:00:00
        #PBS -l walltime={walltime_hours}:00:00
        #PBS -j oe
        #PBS -l mem={memgb}gb
        #PBS -N "dnorm_{chunk_num}"
        #PBS -o dnorm_chunk{chunk_num}.out
        #PBS -m n

        # python 3.4+ required
        module load python/3.5.1

        # move to bioshovel directory and activate venv
        cd {bioshovel_dir}
        source venv/bin/activate

        # run preprocess.disease_ner
        cd src
        python3 -m preprocess.disease_ner {input_paragraph_path} {output_dir} --dnorm {dnorm} --logdir {job_log_directory} --notqdm --poolsize {poolsize}

        STATUS=$?
        if [ $STATUS -ne 0 ]; then
          echo "Disease NER (DNorm) failed"; exit $STATUS
        else
          echo "Finished successfully!"
        fi
        ''').strip('\n').format(**cust_dict)

    job_file_path = os.path.join(job_dir, 'disease_ner_chunk{}.job'.format(chunk_num))
    with open(job_file_path, 'w') as f:
        f.write(pbs_jobfile)

    return job_file_path

def main(args):

    # make all paths absolute (to simplify things later)
    args.paragraph_path = os.path.abspath(args.paragraph_path)
    args.output_directory = os.path.abspath(args.output_directory)
    args.logdir = os.path.abspath(args.logdir)
    args.dnorm = os.path.abspath(args.dnorm)
    args.bioshovel = os.path.abspath(args.bioshovel)

    file_exists_or_exit(os.path.join(args.dnorm, 'ApplyDNorm.sh'))

    # calculate how many Java/DNorm processes to start, given available RAM
    # (DNorm requires 10GB RAM per process)
    args.poolsize = calc_dnorm_num_processes(num_cores=args.poolsize,
                                             ram_gb=args.memgb)

    # get all files (recursive)
    print('Organizing input files and submitting jobs...')
    if args.resume:
        # filter out filenames that are already done...
        args.resume = os.path.abspath(args.resume)
        file_exists_or_exit(args.resume)
        print('Resuming job submission from path: {}'.format(args.resume))

        if os.path.exists(args.output_directory):
            print('Output directory changed to avoid file conflicts:')
            print('OLD: '+args.output_directory)
            args.output_directory += '_resume'
            print('NEW: '+args.output_directory)

        print('Reading previously completed files...')
        # this set may use a lot of RAM if args.resume path contains a ton of files...
        done_files = set(p.name for p in tqdm(Path(args.resume).glob('**/*')) if p.is_file())

        all_files = (str(f) for f in tqdm(Path(args.paragraph_path).glob('**/*')) if f.is_file() and f.name not in done_files)
    else:
        all_files = (str(f) for f in tqdm(Path(args.paragraph_path).glob('**/*')) if f.is_file())

    # divide list into chunks of size n
    filelist_with_sublists = create_sublists_sized_n(all_files, args.nfiles)

    # move job files into the appropriate subdirectories
    #   (don't store more than 1k per sub-subdirectory)
    # create job file for each subdirectory
    # submit jobs
    base_input_directory = os.path.join(args.output_directory, 'input_files')
    job_dir = os.path.join(args.output_directory, 'job_files')
    output_directory = os.path.join(args.output_directory, 'output')
    for path in (base_input_directory, job_dir, output_directory):
        ensure_path_exists(path)
    job_file_paths_failed = []
    jobs_submitted_success = 0
    for sublist_num, sublist in enumerate(filelist_with_sublists):
        sublist_dir = os.path.join(base_input_directory, 
                                   'sublist_{0:0>4}'.format(sublist_num))
        ensure_path_exists(sublist_dir)
        create_sublist_symlinks(sublist, sublist_dir, 1000)
        job_file_path = create_job_file(job_dir, sublist_dir, output_directory, sublist_num, args)
        if args.submit:
            result = submit_pbs_job(job_file_path, queue=args.queue)
            if result:
                jobs_submitted_success += 1
            else:
                job_file_paths_failed.append(job_file_path)

    print('Successfully submitted {} jobs with {} failed submissions'.format(jobs_submitted_success,
                                                                             len(job_file_paths_failed)))
    for path in job_file_paths_failed:
        print('FAILED TO SUBMIT', path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run preprocess.chem_ner as a collection of cluster jobs')
    parser.add_argument('paragraph_path',
                        help='Directory of parsed paragraph files')
    parser.add_argument('output_directory',
                        help='Final output directory')
    parser.add_argument('--dnorm', help='Directory where ApplyDNorm.sh is located',
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
    parser.add_argument('--nfiles',
                        help='Number of files per PBS job',
                        type=int,
                        default=500)
    parser.add_argument('--poolsize',
                        help='Size of multiprocessing process pool',
                        type=int,
                        default=16)
    parser.add_argument('--memgb',
                        help='Amount of RAM to allocate per PBS job (GB)',
                        type=int,
                        default=94)
    parser.add_argument('--resume',
                        help='Resume job submission based on a previous output directory',
                        type=str)
    args = parser.parse_args()
    main(args)