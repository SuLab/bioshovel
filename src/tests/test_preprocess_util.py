#!/usr/bin/env python3
''' Tests for preprocess util functions:

    preprocess.util
'''

import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

from preprocess import util

class UtilTestCase(unittest.TestCase):

    ''' Some tests for preprocess.util
    '''

    def test_util_save_file_works(self):

        file_lines = ['fileline1\n', 'fileline2\n', 'fileline3\n']
        with tempfile.TemporaryDirectory() as tempdir:
            file_name = 'testfile'
            returned_file_path = util.save_file(file_name, file_lines, tempdir)
            new_file_path = os.path.join(tempdir, file_name)
            self.assertEqual(returned_file_path, new_file_path)
            self.assertTrue(os.path.isfile(new_file_path))

            with open(new_file_path) as f:
                self.assertEqual(len(f.readlines()), 3)

    def test_create_n_sublists(self):

        l = list(range(50))
        chunked_10 = util.create_n_sublists(l, n=10)
        self.assertEqual(len(chunked_10), 10)

        # check sublist sizes (no remainder after splitting)
        chunked_10_sizes_correct = (5,)*10
        chunked_10_sizes = tuple(len(x) for x in chunked_10)
        self.assertEqual(chunked_10_sizes, chunked_10_sizes_correct)

        # check sublists sizes (remainder after splitting)
        chunked_7 = util.create_n_sublists(l, n=7)
        chunked_7_sizes_correct = (8,)+(7,)*6
        chunked_7_sizes = tuple(len(x) for x in chunked_7)
        self.assertEqual(chunked_7_sizes, chunked_7_sizes_correct)

    def test_file_exists_or_exit(self):

        # silence STDERR output from this test
        sys.stderr = StringIO()

        with self.assertRaises(SystemExit) as e:
            util.file_exists_or_exit('/this/file/doesnt/exist')

        self.assertEqual(e.exception.code, 1)

    def test_shell_command_exists_or_exit_fails_with_bogus_command(self):

        ''' a shell command that doesn't exist should cause a python call to
            sys.exit(1)
        '''

        # silence STDERR output from this test
        sys.stderr = StringIO()

        with self.assertRaises(SystemExit) as e:
            util.shell_command_exists_or_exit('asdfasf') # fake shell command

        self.assertEqual(e.exception.code, 1)

    def test_shell_command_exists_or_exit_returns_with_real_command(self):

        # silence STDERR output from this test
        sys.stderr = StringIO()

        return_val = util.shell_command_exists_or_exit('python3')
        self.assertTrue(return_val)

    def test_shell_command_exists_or_exit_returns_with_real_two_part_command(self):

        ''' trying to run this command with a 2+ part expression (such as 
            `python3 some_script.py` should only check the first portion, 
            `python3`)
        '''

        # silence STDERR output from this test
        sys.stderr = StringIO()

        # should only use the 'python3' portion of the command
        return_val = util.shell_command_exists_or_exit('python3 some_script.py')
        self.assertTrue(return_val)

    def test_ensure_path_exists_creates_a_nonexistent_path(self):

        with tempfile.TemporaryDirectory() as tmpdirname:
            new_dir = os.path.join(tmpdirname, 'new_directory')
            util.ensure_path_exists(new_dir)
            self.assertTrue(os.path.isdir(new_dir))

    def test_reorganize_directory_works_properly(self):

        ''' reorganize_directory() should take an input directory with a number
            of subfiles and create subdirectories+move files such that no
            subdirectory has > max_files_per_subdir files
        '''

        with tempfile.TemporaryDirectory() as tmpdirname:
            for i in range(10):
                with open(os.path.join(tmpdirname, 'test{}'.format(i)), 'w') as f:
                    pass
            util.reorganize_directory(tmpdirname,
                                      max_files_per_subdir=2,
                                      quiet=True)
            tmppath = Path(tmpdirname)
            subfiles = list(tmppath.glob('**/*'))
            num_dirs = len([f for f in subfiles if f.is_dir()])
            num_files = len([f for f in subfiles if f.is_file()])
            self.assertEqual(num_dirs, 5)
            self.assertEqual(num_files, 10)

    def test_calc_dnorm_num_processes(self):

        ''' test that the number of processes is returned correctly, given
            appropriate inputs
        '''

        # Given a machine with 16 CPU cores and 80GB RAM, only 8 DNorm
        # processes should be launched (10GB per process)
        self.assertEqual(util.calc_dnorm_num_processes(num_cores=16, ram_gb=80),
                         8)

        # Given a machine with 16 CPU cores and 200GB RAM, 16 DNorm
        # processes should be launched (> 10GB per process available)
        self.assertEqual(util.calc_dnorm_num_processes(num_cores=16, ram_gb=200),
                         16)

    def test_get_file_lines_set(self):

        data = ['12345', '23456', '34567']

        # test getting file lines as set of strings
        with tempfile.NamedTemporaryFile() as f:
            str_data = '\n'.join(data)+'\n'
            f.write(str_data.encode('utf-8'))
            f.seek(0)
            result = util.get_file_lines_set(f.name)
            self.assertEqual(set(data), result)

        # test getting file lines as set of ints
        with tempfile.NamedTemporaryFile() as f:
            str_data = '\n'.join(data)+'\n'
            f.write(str_data.encode('utf-8'))
            f.seek(0)
            result = util.get_file_lines_set(f.name, typecast=int)
            self.assertEqual(set(int(d) for d in data), result)