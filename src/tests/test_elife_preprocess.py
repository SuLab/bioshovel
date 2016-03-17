#!/usr/bin/env python3

import os
import tempfile
import textwrap
import unittest
from bs4 import BeautifulSoup
from preprocess import parse_elife_xml
from tests.elife_sample_article import xml_file_string as sample_xml

class ELifeParserTestCase(unittest.TestCase):

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.xml_string = sample_xml
        
        self.tmpfile.write(self.xml_string)
        self.tmpfile.close()

    def tearDown(self):
        os.unlink(self.tmpfile.name)

class ELifeParserSoupTests(ELifeParserTestCase):

    def test_read_file_returns_soup_object(self):

        ''' Test that read_file() returns a BeautifulSoup object
        '''

        soup = parse_elife_xml.read_file(self.tmpfile.name)
        self.assertIsInstance(soup, BeautifulSoup)

class ELifeParserExtractorTests(ELifeParserTestCase):

    ''' Class for testing various aspects of the eLife XML parser

        Test assertions are based on parsing of the following eLife article XML:

        Dambacher, et al. 2016
        Atomic structure of the 26S proteasome lid reveals the mechanism of 
        deubiquitinase inhibition

        DOI: 10.7554/elife.13027
    '''

    def setUp(self):
        super().setUp()
        self.soup = parse_elife_xml.read_file(self.tmpfile.name)

    def test_body_tag_replaced_with_bodyreplaced(self):

        ''' Tests that the <body> tag was replaced with <bodyreplaced>,
            along with accompanying closing tags

            (this is the make things easier using the lxml parser)
        '''

        found_tag = self.soup.find('bodyreplaced')
        self.assertTrue(found_tag)

    def only_one_body_tag_found(self):
        found_tag = self.soup.find_all('body')
        self.assertEqual(len(found_tag), 1)

    def test_get_doi_escaped(self):
        doi = parse_elife_xml.get_doi(self.soup)
        self.assertEqual(doi, '10.7554%2Felife.13027')

    def test_get_doi_returns_right_value(self):
        doi = parse_elife_xml.get_doi(self.soup, escape_slash=False)
        self.assertEqual(doi, '10.7554/elife.13027')

    def test_get_title(self):
        title = parse_elife_xml.get_title(self.soup)
        self.assertEqual(title, 'Atomic structure of the 26S proteasome lid reveals the mechanism of deubiquitinase inhibition')

    def test_get_abstract(self):
        abstract = parse_elife_xml.get_abstract(self.soup)

        abstract_start = abstract[:50]
        abstract_end = abstract[-50:]
        correct_abstract_start = 'The 26S proteasome is responsible for the selectiv'
        correct_abstract_end = 'ates the deubiquitinase for substrate degradation.'
        
        # check beginning and end because maxDiff is much shorter than abstract
        self.assertEqual(abstract_start, correct_abstract_start)
        self.assertEqual(abstract_end, correct_abstract_end)

    def test_get_correct_number_of_main_article_paragraphs(self):
        article_paragraphs = parse_elife_xml.get_main_article(self.soup, 
                                                              keep_references=True)
        
        self.assertEqual(len(article_paragraphs), 59)

    def test_get_main_article_returns_correct_text(self):
        article_paragraphs = parse_elife_xml.get_main_article(self.soup)
        first_paragraph_start_text = 'The eukaryotic 26S proteasome is a large multi-enzyme'
        last_paragraph_end_text = 'been deposited under accession ID: 3JCK in the PDB.'

        correct_beginning = article_paragraphs[0].startswith(first_paragraph_start_text)
        correct_ending = article_paragraphs[-1].endswith(last_paragraph_end_text)

        self.assertTrue(correct_beginning)
        self.assertTrue(correct_ending)

    def test_get_main_article_with_references(self):
        article_paragraphs = parse_elife_xml.get_main_article(self.soup, 
                                                              keep_references=True)

        text_with_article_ref = 'removed by the proteasome (Finley, 2009). The barrel-shaped core peptidase'

        text_found_in_paragraph = text_with_article_ref in article_paragraphs[0]

        self.assertTrue(text_found_in_paragraph)

    def test_get_main_article_without_references_article_ref_removed(self):

        ''' Checks that article references were correctly removed from text
        '''

        article_paragraphs = parse_elife_xml.get_main_article(self.soup, 
                                                              keep_references=False)

        text_with_article_ref = 'removed by the proteasome. The barrel-shaped core peptidase'

        text_found_in_paragraph = text_with_article_ref in article_paragraphs[0]

        self.assertTrue(text_found_in_paragraph)

    def test_get_main_article_without_references_figure_ref_removed(self):

        ''' Checks that figure references were correctly removed from text
        '''

        article_paragraphs = parse_elife_xml.get_main_article(self.soup, 
                                                              keep_references=False)

        text_with_figure_ref = 'determined by cryo-electron microscopy (cryoEM), revealing the molecular'

        text_found_in_paragraph = text_with_figure_ref in article_paragraphs[3]

        self.assertTrue(text_found_in_paragraph)
