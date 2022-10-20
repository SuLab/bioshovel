#!/usr/bin/env python3

# for creating a dictionary of gold standard relations from the biocreative
# training corpus... (tgz)
#
# run using:
# cd [bioshovel/src/deepdive]
# `deepdive env python3 misc/extract_cid_relations.py`

import glob
import os
os.chdir(os.environ['CURRENT_DD_APP'])
import sys
import tarfile
import tempfile
from udf.pubtator_parse import PubtatorParser
from udf.util import filter_files_from_tar

def main():

    article_archive = '../../data/biocreative_cdr_training_0_combined.tgz'
    token_pairs = set()
    with tarfile.open(article_archive, "r:gz") as tar, tempfile.TemporaryDirectory() as td:

        pubtator_files = filter_files_from_tar(tar, 'pubtator_cid')

        # extract pubtator and corenlp output files into tempdir
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, path=td, members=pubtator_files)

        pubtator_filepaths = sorted(glob.glob(os.path.join(td,
                                                           '*',
                                                           'pubtator_cid',
                                                           '*')))

        for filepath in pubtator_filepaths:
            parser = PubtatorParser(filepath)
            parser.make_mesh_token_lookup()
            for m1, m2 in parser.cid_ground_truth_ids:
                token_pairs.add(parser.mesh_dict.get(m1)+'\t'+parser.mesh_dict.get(m2))

    with open('cid_relation_tokens.tsv.txt', 'w') as f:
        for pair in token_pairs:
            f.write(pair+'\n')

if __name__ == '__main__':
    main()
