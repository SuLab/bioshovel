#!/usr/bin/env python3

# Tests for Name-Entity Recognition scripts:
#
# chem_ner.py
# disease_ner.py
# gene_ner.py
# util.py

import os
import tempfile
import textwrap
import unittest
from queue import Queue

from preprocess import (chem_ner,
                        reformat,
                        util)

class UtilTestCase(unittest.TestCase):

    ''' Some tests for preprocess.util
    '''

    def test_util_save_file_works(self):

        file_lines = ['fileline1\n', 'fileline2\n', 'fileline3\n']
        with tempfile.TemporaryDirectory() as tempdir:
            file_name = 'testfile'
            util.save_file(file_name, file_lines, tempdir)
            new_file_path = os.path.join(tempdir, file_name)
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

class NERTestCase(unittest.TestCase):

    def setUp(self):
        self.parfile_string = textwrap.dedent('''
            title\tMolecular architecture of human polycomb repressive complex 2
            abs\tPolycomb Repressive Complex 2 (PRC2) is essential for gene silencing, establishing transcriptional repression of specific genes by tri-methylating Lysine 27 of histone H3, a process mediated by cofactors such as AEBP2. In spite of its biological importance, little is known about PRC2 architecture and subunit organization. Here, we present the first three-dimensional electron microscopy structure of the human PRC2 complex bound to its cofactor AEBP2. Using a novel internal protein tagging-method, in combination with isotopic chemical cross-linking and mass spectrometry, we have localized all the PRC2 subunits and their functional domains and generated a detailed map of interactions. The position and stabilization effect of AEBP2 suggests an allosteric role of this cofactor in regulating gene silencing. Regions in PRC2 that interact with modified histone tails are localized near the methyltransferase site, suggesting a molecular mechanism for the chromatin-based regulation of PRC2 activity.
            p\tProtein complexes--stable structures that contain two or more proteins--have an important role in the biochemical processes that are associated with the expression of genes. Some help to silence genes, whereas others are involved in the activation of genes. The importance of such complexes is emphasized by the fact that mice die as embryos, or are born with serious defects, if they do not possess the protein complex known as Polycomb Repressive Complex 2, or PRC2 for short.
            p\tIt is known that the core of this complex, which is found in species that range from           Drosophila          to humans, is composed of four different proteins, and that the structures of two of these have been determined with atomic precision. It is also known that PRC2 requires a particular protein co-factor (called AEBP2) to perform this function. Moreover, it has been established that PRC2 silences genes by adding two or three methyl (CH3) groups to a particular amino acid (Lysine 27) in one of the proteins (histone H3) that DNA strands wrap around in the nucleus of cells. However, despite its biological importance, little is known about the detailed architecture of PRC2.
            p\tCiferri et al. shed new light on the structure of this complex by using electron microscopy to produce the first three-dimensional image of the human PRC2 complex bound to its cofactor. By incorporating various protein tags into the co-factor and the four subunits of the PRC2, and by employing mass spectrometry and other techniques, Ciferri et al. were able to identify 60 or so interaction sites within the PRC2-cofactor system, and to determine their locations within the overall structure.
        ''')

        # self.parfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
        # self.xml_string = sample_xml
        
        # self.tmpfile.write(self.xml_string)
        # self.tmpfile.close()

    def tearDown(self):
        pass
    #     # os.unlink(self.tmpfile.name)

