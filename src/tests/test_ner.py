#!/usr/bin/env python3
''' Tests for Name-Entity Recognition scripts:

    chem_ner.py
    disease_ner.py
    gene_ner.py
'''

import os
import sys
import tempfile
import textwrap
import unittest
from io import StringIO
from pathlib import Path
from queue import Queue

from preprocess import (chem_ner,
                        reformat)

class ReformatTestCase(unittest.TestCase):

    def setUp(self):
        self.escaped_doi = '10.7554%2FeLife.00005'
        self.title_line = 'title\tMolecular architecture of human polycomb repressive complex 2'
        self.body = ['abs\tPolycomb Repressive Complex 2 (PRC2) is essential for gene silencing, establishing transcriptional repression of specific genes by tri-methylating Lysine 27 of histone H3, a process mediated by cofactors such as AEBP2. In spite of its biological importance, little is known about PRC2 architecture and subunit organization. Here, we present the first three-dimensional electron microscopy structure of the human PRC2 complex bound to its cofactor AEBP2. Using a novel internal protein tagging-method, in combination with isotopic chemical cross-linking and mass spectrometry, we have localized all the PRC2 subunits and their functional domains and generated a detailed map of interactions. The position and stabilization effect of AEBP2 suggests an allosteric role of this cofactor in regulating gene silencing. Regions in PRC2 that interact with modified histone tails are localized near the methyltransferase site, suggesting a molecular mechanism for the chromatin-based regulation of PRC2 activity.',
                     'p\tProtein complexes--stable structures that contain two or more proteins--have an important role in the biochemical processes that are associated with the expression of genes. Some help to silence genes, whereas others are involved in the activation of genes. The importance of such complexes is emphasized by the fact that mice die as embryos, or are born with serious defects, if they do not possess the protein complex known as Polycomb Repressive Complex 2, or PRC2 for short.',
                     'p\tIt is known that the core of this complex, which is found in species that range from           Drosophila          to humans, is composed of four different proteins, and that the structures of two of these have been determined with atomic precision. It is also known that PRC2 requires a particular protein co-factor (called AEBP2) to perform this function. Moreover, it has been established that PRC2 silences genes by adding two or three methyl (CH3) groups to a particular amino acid (Lysine 27) in one of the proteins (histone H3) that DNA strands wrap around in the nucleus of cells. However, despite its biological importance, little is known about the detailed architecture of PRC2.',
                     'p\tCiferri et al. shed new light on the structure of this complex by using electron microscopy to produce the first three-dimensional image of the human PRC2 complex bound to its cofactor. By incorporating various protein tags into the co-factor and the four subunits of the PRC2, and by employing mass spectrometry and other techniques, Ciferri et al. were able to identify 60 or so interaction sites within the PRC2-cofactor system, and to determine their locations within the overall structure.']
        self.parfile_string = textwrap.dedent('''
            title\tMolecular architecture of human polycomb repressive complex 2
            abs\tPolycomb Repressive Complex 2 (PRC2) is essential for gene silencing, establishing transcriptional repression of specific genes by tri-methylating Lysine 27 of histone H3, a process mediated by cofactors such as AEBP2. In spite of its biological importance, little is known about PRC2 architecture and subunit organization. Here, we present the first three-dimensional electron microscopy structure of the human PRC2 complex bound to its cofactor AEBP2. Using a novel internal protein tagging-method, in combination with isotopic chemical cross-linking and mass spectrometry, we have localized all the PRC2 subunits and their functional domains and generated a detailed map of interactions. The position and stabilization effect of AEBP2 suggests an allosteric role of this cofactor in regulating gene silencing. Regions in PRC2 that interact with modified histone tails are localized near the methyltransferase site, suggesting a molecular mechanism for the chromatin-based regulation of PRC2 activity.
            p\tProtein complexes--stable structures that contain two or more proteins--have an important role in the biochemical processes that are associated with the expression of genes. Some help to silence genes, whereas others are involved in the activation of genes. The importance of such complexes is emphasized by the fact that mice die as embryos, or are born with serious defects, if they do not possess the protein complex known as Polycomb Repressive Complex 2, or PRC2 for short.
            p\tIt is known that the core of this complex, which is found in species that range from           Drosophila          to humans, is composed of four different proteins, and that the structures of two of these have been determined with atomic precision. It is also known that PRC2 requires a particular protein co-factor (called AEBP2) to perform this function. Moreover, it has been established that PRC2 silences genes by adding two or three methyl (CH3) groups to a particular amino acid (Lysine 27) in one of the proteins (histone H3) that DNA strands wrap around in the nucleus of cells. However, despite its biological importance, little is known about the detailed architecture of PRC2.
            p\tCiferri et al. shed new light on the structure of this complex by using electron microscopy to produce the first three-dimensional image of the human PRC2 complex bound to its cofactor. By incorporating various protein tags into the co-factor and the four subunits of the PRC2, and by employing mass spectrometry and other techniques, Ciferri et al. were able to identify 60 or so interaction sites within the PRC2-cofactor system, and to determine their locations within the overall structure.
        ''').lstrip('\n')

    def tearDown(self):
        pass

class ParformToPubtatorTests(ReformatTestCase):

    def test_parform_to_pubtator_format_is_correct(self):
        pubtator_file_lines = reformat.parform_to_pubtator(self.escaped_doi,
                                                           self.title_line,
                                                           self.body)

        title_line_1 = self.escaped_doi+'_a|t|Molecular architecture of human polycomb repressive complex 2'
        abstract_line_1 = self.escaped_doi+'_a|a|Polycomb Repressive Complex 2 (PRC2) is essential for gene silencing, establishing transcriptional repression of specific genes by tri-methylating Lysine 27 of histone H3, a process mediated by cofactors such as AEBP2. In spite of its biological importance, little is known about PRC2 architecture and subunit organization. Here, we present the first three-dimensional electron microscopy structure of the human PRC2 complex bound to its cofactor AEBP2. Using a novel internal protein tagging-method, in combination with isotopic chemical cross-linking and mass spectrometry, we have localized all the PRC2 subunits and their functional domains and generated a detailed map of interactions. The position and stabilization effect of AEBP2 suggests an allosteric role of this cofactor in regulating gene silencing. Regions in PRC2 that interact with modified histone tails are localized near the methyltransferase site, suggesting a molecular mechanism for the chromatin-based regulation of PRC2 activity.'
        abstract_line_2 = self.escaped_doi+'_1|a|Protein complexes--stable structures that contain two or more proteins--have an important role in the biochemical processes that are associated with the expression of genes. Some help to silence genes, whereas others are involved in the activation of genes. The importance of such complexes is emphasized by the fact that mice die as embryos, or are born with serious defects, if they do not possess the protein complex known as Polycomb Repressive Complex 2, or PRC2 for short.'

        file_lines = pubtator_file_lines[1]

        self.assertEqual(file_lines[0][:50], title_line_1[:50])
        self.assertEqual(file_lines[1][:50], abstract_line_1[:50])
        self.assertEqual(file_lines[4][:50], abstract_line_2[:50])

    def test_parform_to_pubtator_removes_pipe_char(self):

        ''' pipe characters cause problems with some pubtator tools
        '''

        self.body[0] = 'abs\tPolycomb Repressive Complex 2 (PR|C2) is essential for gene silencing, establishing transcriptional repression of specific genes by tri-methylating Lysine 27 of histone H3, a process mediated by cofactors such as AEBP2. In spite of its biological importance, little is known about PRC2 architecture and subunit organization. Here, we present the first three-dimensional electron microscopy structure of the human PRC2 complex bound to its cofactor AEBP2. Using a novel internal protein tagging-method, in combination with isotopic chemical cross-linking and mass spectrometry, we have localized all the PRC2 subunits and their functional domains and generated a detailed map of interactions. The position and stabilization effect of AEBP2 suggests an allosteric role of this cofactor in regulating gene silencing. Regions in PRC2 that interact with modified histone tails are localized near the methyltransferase site, suggesting a molecular mechanism for the chromatin-based regulation of PRC2 activity.'
        correct = self.escaped_doi+'_a|a|Polycomb Repressive Complex 2 (PRC2) is essential for gene silencing, establishing transcriptional repression of specific genes by tri-methylating Lysine 27 of histone H3, a process mediated by cofactors such as AEBP2. In spite of its biological importance, little is known about PRC2 architecture and subunit organization. Here, we present the first three-dimensional electron microscopy structure of the human PRC2 complex bound to its cofactor AEBP2. Using a novel internal protein tagging-method, in combination with isotopic chemical cross-linking and mass spectrometry, we have localized all the PRC2 subunits and their functional domains and generated a detailed map of interactions. The position and stabilization effect of AEBP2 suggests an allosteric role of this cofactor in regulating gene silencing. Regions in PRC2 that interact with modified histone tails are localized near the methyltransferase site, suggesting a molecular mechanism for the chromatin-based regulation of PRC2 activity.'

        pubtator_file_lines = reformat.parform_to_pubtator(self.escaped_doi,
                                                           self.title_line,
                                                           self.body)

        self.assertEqual(pubtator_file_lines[1][1][:50], correct[:50])

class NERTempFileTestCase(ReformatTestCase):

    ''' Subclass that has a 'parfile' saved as a temporary file
    '''

    def setUp(self):
        super().setUp()
        self.tmpdir = tempfile.TemporaryDirectory()
        self.filepath = os.path.join(self.tmpdir.name, self.escaped_doi)
        with open(self.filepath, 'w') as f:
            f.write(self.parfile_string)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_parform_parses_DOI_title_body_correctly(self):
        parsed = reformat.parse_parform_file(self.filepath)

        # parse_parform_file should return a triple
        self.assertTrue(len(parsed) == 3)
        doi, title, body = parsed

        # DOI should be correct
        self.assertEqual(doi, self.escaped_doi)

        # title line should be correct
        self.assertEqual(self.title_line, title)

        # body should have 4 items, the first starting with 'abs' and the other
        # 3 starting with 'p'
        self.assertTrue(len(body) == 4)
        self.assertTrue(body[0].startswith('abs\t'))
        self.assertTrue(all(line.startswith('p\t') for line in body[1:]))

class ParformToPlaintextTests(ReformatTestCase):

    ''' Some tests for the reformat.parform_to_plaintext function
    '''

    def setUp(self):
        super().setUp()

        self.correct_title_line = 'Molecular architecture of human polycomb repressive complex 2'
        self.correct_first_paragraph_line = 'Polycomb Repressive Complex 2 (PRC2) is essential for gene silencing, establishing transcriptional repression of specific genes by tri-methylating Lysine 27 of histone H3, a process mediated by cofactors such as AEBP2. In spite of its biological importance, little is known about PRC2 architecture and subunit organization. Here, we present the first three-dimensional electron microscopy structure of the human PRC2 complex bound to its cofactor AEBP2. Using a novel internal protein tagging-method, in combination with isotopic chemical cross-linking and mass spectrometry, we have localized all the PRC2 subunits and their functional domains and generated a detailed map of interactions. The position and stabilization effect of AEBP2 suggests an allosteric role of this cofactor in regulating gene silencing. Regions in PRC2 that interact with modified histone tails are localized near the methyltransferase site, suggesting a molecular mechanism for the chromatin-based regulation of PRC2 activity.'
        self.correct_last_paragraph_line = 'Ciferri et al. shed new light on the structure of this complex by using electron microscopy to produce the first three-dimensional image of the human PRC2 complex bound to its cofactor. By incorporating various protein tags into the co-factor and the four subunits of the PRC2, and by employing mass spectrometry and other techniques, Ciferri et al. were able to identify 60 or so interaction sites within the PRC2-cofactor system, and to determine their locations within the overall structure.'

    def test_parform_to_plaintext_reformat_is_correct(self):

        plaintext_file_lines = reformat.parform_to_plaintext(self.title_line,
                                                             self.body)

        title_line = plaintext_file_lines[0].rstrip('\n')
        self.assertEqual(title_line[:50], self.correct_title_line[:50])

        first_paragraph_line = plaintext_file_lines[1].rstrip('\n')
        self.assertEqual(first_paragraph_line[:50],
                         self.correct_first_paragraph_line[:50])

        last_paragraph_line = plaintext_file_lines[-1].rstrip('\n')
        self.assertEqual(last_paragraph_line[:50],
                         self.correct_last_paragraph_line[:50])

    def test_parform_to_plaintext_reformat_adds_period_after_title(self):

        ''' if period_following_title kwarg is True, the returned title line 
            should have a period after it

            (helps with CoreNLP sentence splitting of title line 
            from sentence 1)
        '''

        plaintext_file_lines = reformat.parform_to_plaintext(self.title_line,
                                                             self.body,
                                                             period_following_title=True)

        title_line = plaintext_file_lines[0].rstrip('\n')
        correct_title_line_with_period = self.correct_title_line + '.'
        self.assertEqual(title_line[-50:], correct_title_line_with_period[-50:])

    def test_parform_to_plaintext_reformat_does_not_add_period_after_title_ending_in_period(self):

        ''' if period_following_title kwarg is True, the returned title line 
            should have a period after it -- UNLESS the title already ends with
            a period (in that case, leave it as-is)
        '''

        plaintext_file_lines = reformat.parform_to_plaintext(self.title_line+'.',
                                                             self.body,
                                                             period_following_title=True)

        title_line = plaintext_file_lines[0].rstrip('\n')
        correct_title_line_with_period = self.correct_title_line + '.'
        self.assertEqual(title_line[-50:], correct_title_line_with_period[-50:])

    def test_parform_to_plaintext_reformat_adds_newlines_correctly(self):

        ''' if newlines kwarg is True, each line of the output should have an empty
            newline after it
        '''

        plaintext_file_lines = reformat.parform_to_plaintext(self.title_line,
                                                             self.body,
                                                             newlines=True)
        even_numbered_lines = plaintext_file_lines[1::2]
        staggered_newlines_present = all([line=='\n' for line in even_numbered_lines])
        self.assertTrue(staggered_newlines_present)

class PubtatorInputTests(ReformatTestCase):

    ''' Some tests for functions:
        reformat.pubtator_to_plaintext
        reformat.pubtator_to_parform
    '''

    def setUp(self):
        super().setUp()
        self.pubtator_title = '3513765|t|Protein kinase C desensitization by phorbol esters and its impact on growth of human breast cancer cells.'
        self.pubtator_abstract = '3513765|a|Active phorbol esters such as TPA (12-0-tetra-decanoylphorbol-13-acetate) inhibited growth of mammary carcinoma cells (MCF-7 greater than BT-20 greater than MDA-MB-231 greater than = ZR-75-1 greater than HBL-100) with the exception of T-47-D cells presumably by interacting with the phospholipid/Ca2+-dependent protein kinase (PKC). The nonresponsive T-47-D cells exhibited the lowest PKC activity. A rapid (30 min) TPA-dependent translocation of cytosolic PKC to membranes was found in the five TPA-sensitive cell without affecting cell growth. However, TPA-treatment of more than 10 hours inhibited reversibly the growth of TPA-responsive cells. This effect coincided with the complete loss of cellular PKC activity due to the proteolysis of the translocated membrane-bound PKC holoenzyme (75K) into 60K and 50K PKC fragments. Resumption of cell growth after TPA-removal was closely related to the specific reappearance of the PKC holoenzyme activity (75K) in the TPA-responsive human mammary tumor cell lines suggesting an involvement of PKC in growth regulation.'
        self.stripped_title = 'Protein kinase C desensitization by phorbol esters and its impact on growth of human breast cancer cells.'
        self.stripped_abstract = 'Active phorbol esters such as TPA (12-0-tetra-decanoylphorbol-13-acetate) inhibited growth of mammary carcinoma cells (MCF-7 greater than BT-20 greater than MDA-MB-231 greater than = ZR-75-1 greater than HBL-100) with the exception of T-47-D cells presumably by interacting with the phospholipid/Ca2+-dependent protein kinase (PKC). The nonresponsive T-47-D cells exhibited the lowest PKC activity. A rapid (30 min) TPA-dependent translocation of cytosolic PKC to membranes was found in the five TPA-sensitive cell without affecting cell growth. However, TPA-treatment of more than 10 hours inhibited reversibly the growth of TPA-responsive cells. This effect coincided with the complete loss of cellular PKC activity due to the proteolysis of the translocated membrane-bound PKC holoenzyme (75K) into 60K and 50K PKC fragments. Resumption of cell growth after TPA-removal was closely related to the specific reappearance of the PKC holoenzyme activity (75K) in the TPA-responsive human mammary tumor cell lines suggesting an involvement of PKC in growth regulation.'
        self.abstract_id = '3513765'
        self.parform_title = 'title\tProtein kinase C desensitization by phorbol esters and its impact on growth of human breast cancer cells.'
        self.parform_abstract = 'abs\tActive phorbol esters such as TPA (12-0-tetra-decanoylphorbol-13-acetate) inhibited growth of mammary carcinoma cells (MCF-7 greater than BT-20 greater than MDA-MB-231 greater than = ZR-75-1 greater than HBL-100) with the exception of T-47-D cells presumably by interacting with the phospholipid/Ca2+-dependent protein kinase (PKC). The nonresponsive T-47-D cells exhibited the lowest PKC activity. A rapid (30 min) TPA-dependent translocation of cytosolic PKC to membranes was found in the five TPA-sensitive cell without affecting cell growth. However, TPA-treatment of more than 10 hours inhibited reversibly the growth of TPA-responsive cells. This effect coincided with the complete loss of cellular PKC activity due to the proteolysis of the translocated membrane-bound PKC holoenzyme (75K) into 60K and 50K PKC fragments. Resumption of cell growth after TPA-removal was closely related to the specific reappearance of the PKC holoenzyme activity (75K) in the TPA-responsive human mammary tumor cell lines suggesting an involvement of PKC in growth regulation.'

    def test_pubtator_to_plaintext_parses_record(self):

        plaintext_file_lines = reformat.pubtator_to_plaintext(self.pubtator_title,
                                                              self.pubtator_abstract)
        self.assertEqual(plaintext_file_lines[0][:25], self.stripped_title[:25])
        self.assertEqual(plaintext_file_lines[1][:25], self.stripped_abstract[:25])
        self.assertEqual(plaintext_file_lines[1][-25:], self.stripped_abstract[-25:])

    def test_pubtator_to_plaintext_adds_newlines_correctly(self):

        ''' if newlines kwarg is True, each line of output should have a
            trailing newline character
        '''

        plaintext_file_lines = reformat.pubtator_to_plaintext(self.pubtator_title,
                                                              self.pubtator_abstract,
                                                              newlines=True)
        self.assertTrue(plaintext_file_lines[0].endswith('\n'))
        self.assertTrue(plaintext_file_lines[1].endswith('\n'))

    def test_pubtator_to_parform_parses_record(self):

        parform_output = reformat.pubtator_to_parform(self.pubtator_title,
                                                      self.pubtator_abstract)
        abs_id, (title, abstract) = parform_output
        self.assertEqual(abs_id, self.abstract_id)
        self.assertEqual(title[:25], self.parform_title[:25])
        self.assertEqual(abstract[:25], self.parform_abstract[:25])

    def test_pubtator_to_parform_adds_newlines_correctly(self):

        parform_output = reformat.pubtator_to_parform(self.pubtator_title,
                                                      self.pubtator_abstract,
                                                      newlines=True)
        abs_id, (title, abstract) = parform_output

        self.assertTrue(title.endswith('\n'))
        self.assertTrue(abstract.endswith('\n'))