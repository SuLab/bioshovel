#!/usr/bin/env python3
'''
prep_corenlp.py

Sample usage:
$ python3 -m preprocess.prep_corenlp /gpfs/group/su/sandip/corpus/elife/paragraphs ../data --corenlp /gpfs/group/su/sandip/stanford_corenlp/stanford-corenlp-full-2015-12-09 --submit

Prepares a corpus in paragraph format for processing with Stanford CoreNLP

For use on a PBS cluster (tested on Scripps Garibaldi cluster)

Submits jobs if --submit flag is used.
'''

import argparse
import os
import sys
import subprocess
import textwrap
from glob import glob
from tqdm import tqdm

from preprocess.util import (create_n_sublists,
                             ensure_path_exists,
                             file_exists_or_exit,
                             save_file,
                             shell_command_exists_or_exit)
from preprocess.reformat import (parform_to_plaintext,
                                 parse_parform_file)

def create_job_file(input_files, job_dir, output_dir, chunk_num, args):

    ''' Creates a PBS job file in args.output_directory for the given
        file_list of input files
    '''

    filelist_path = os.path.join(job_dir, 'file_list{}'.format(chunk_num))
    with open(filelist_path, 'w') as f:
        f.writelines(line+'\n' for line in input_files)

    cust_dict = {'output_dir': output_dir,
                 'filelist_path': filelist_path,
                 'chunk_num': chunk_num,
                 'corenlp_dir': args.corenlp,
                 'files_for_processing': [os.path.basename(filepath) for filepath in input_files]
                 }

    pbs_jobfile = textwrap.dedent('''
        #!/bin/bash
        #PBS -l nodes=1:ppn=8
        #PBS -l cput=192:00:00
        #PBS -l walltime=24:00:00
        #PBS -j oe
        #PBS -l mem=8gb
        #PBS -N "corenlp_{chunk_num}"
        #PBS -o corenlp_chunk{chunk_num}.out
        #PBS -m n
          
        echo "############################################################"
        echo "Processing files:"
        echo {files_for_processing}
        echo "############################################################"

        # java 8 required for CoreNLP          
        module load java/1.8.0_65

        # move to Stanford CoreNLP installation directory
        cd {corenlp_dir}

        ./corenlp.sh -outputFormat json -outputDirectory {output_dir} -filelist {filelist_path} -annotators tokenize,ssplit,pos,lemma,ner,parse
        STATUS=$?
        if [ $STATUS -ne 0 ]; then
          echo "CoreNLP failed"; exit $STATUS
        else
          echo "Finished successfully!"
        fi
        ''').strip('\n').format(**cust_dict)

    job_file_path = os.path.join(job_dir, 'corenlp_chunk{}.job'.format(chunk_num))
    with open(job_file_path, 'w') as f:
        f.write(pbs_jobfile)

    return job_file_path

def create_corenlp_input_files(input_files, input_dir):

    ''' Given a list of file paths to parform files (input_files),
        converts files to plaintext format with newlines and saves them to
        directory input_dir.

        Returns a list of file paths to CoreNLP input files.
    '''

    new_files = []
    for parform_file in input_files:
        doi, title, body = parse_parform_file(parform_file)
        plaintext = parform_to_plaintext(title,
                                         body,
                                         newlines=True,
                                         period_following_title=True)
        new_file_path = save_file(doi, plaintext, input_dir)
        new_files.append(new_file_path)

    return new_files

def main(args):
    
    # ensure that `qsub` command exists on this machine...
    shell_command_exists_or_exit('qsub')

    # make paths absolute so that all other paths are also absolute
    args.paragraph_path = os.path.abspath(args.paragraph_path)
    args.output_directory = os.path.abspath(args.output_directory)
    args.corenlp = os.path.abspath(args.corenlp)

    file_exists_or_exit(os.path.join(args.corenlp, 'corenlp.sh'))

    input_dir = os.path.join(args.output_directory, 'input_files')
    job_dir = os.path.join(args.output_directory, 'job_files')
    output_dir = os.path.join(args.output_directory, 'output_files')
    for dirpath in (args.output_directory, input_dir, job_dir, output_dir):
        ensure_path_exists(dirpath)

    all_files = glob(os.path.join(args.paragraph_path, '*'))
    number_of_chunks = len(all_files)//100
    filelist_with_sublists = create_n_sublists(all_files, number_of_chunks)
    job_file_paths = []
    print('Creating {} input files in {} groups with matched job files...'.format(len(all_files),
                                                                                  number_of_chunks))
    for chunk_num, subfilelist in enumerate(tqdm(filelist_with_sublists)):
        new_input_files = create_corenlp_input_files(subfilelist, input_dir)
        new_job_file_path = create_job_file(new_input_files,
                                            job_dir,
                                            output_dir,
                                            chunk_num,
                                            args)
        job_file_paths.append(new_job_file_path)

    print('Created {} PBS job files in {}'.format(len(job_file_paths), job_dir))

    if args.submit:
        print('Submitting jobs to queue \'{}\'...'.format(args.queue))

        job_ids = []
        for job_file in tqdm(job_file_paths):
            try:
                out = subprocess.check_output(['qsub', '-q',
                                               args.queue,
                                               job_file],
                                              cwd=job_dir)
                job_ids.append(out.decode('utf-8').rstrip('\n').split('.')[0])
            except subprocess.CalledProcessError as err:
                string_error = err.output.decode(encoding='UTF-8').rstrip('\n')
                print(string_error, file=sys.stderr)

        print('Submitted {} jobs to queue {}'.format(len(job_ids), args.queue))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Set up files to run Stanford CoreNLP parser on a directory of paragraph-formatted files')
    parser.add_argument('paragraph_path', help='Directory of parsed paragraph files')
    parser.add_argument('output_directory', help='Final output directory')
    parser.add_argument('--corenlp', help='Absolute path for CoreNLP (specifically, where corenlp.sh is located)', default=os.getcwd())
    parser.add_argument('--queue', help='Cluster queue for job submission', default='new')
    parser.add_argument('--submit', help='Submit jobs after creating job files', action='store_true')
    args = parser.parse_args()
    main(args)