#!/usr/bin/env python3

import os
import tempfile
import unittest
from lxml import etree
from preprocess import parse_medline_xml
from tests.medline_sample_xml import sample_medline_xml as sample_xml

class XMLParseBaseClass(unittest.TestCase):

    def setUp(self):
        self.sample_xml = sample_xml

class XMLFileParseTests(XMLParseBaseClass):

    def setUp(self):
        super().setUp()

        self.tempdir = tempfile.TemporaryDirectory()
        self.new_file_path = os.path.join(self.tempdir.name, 'testfile.xml')
        with open(self.new_file_path, 'w') as f:
            f.write(self.sample_xml)

    def tearDown(self):
        super().tearDown()
        self.tempdir.cleanup()

    def test_get_root_object_returns_correctly(self):
        root = parse_medline_xml.get_root_object(self.new_file_path)
        citations = list(root.iter('MedlineCitation'))
        self.assertIs(len(citations), 1)

class XMLParseTests(XMLParseBaseClass):

    def setUp(self):
        super().setUp()
        self.sample_xml = self.sample_xml.encode('utf-8')
        self.root = etree.fromstring(self.sample_xml)

    def test_get_element_works_correctly(self):
        correct_citations = list(self.root.iter('MedlineCitation'))
        test_citations = parse_medline_xml.get_element('MedlineCitation', self.root)
        self.assertEqual(len(correct_citations), len(test_citations))

    def test_abstracttext_subtags_are_combined(self):
        correct_abstract_start = 'The rapid auditory processing defi-cit theory hold'
        correct_abstract_end = 'port the rapid auditory processing deficit theory.'

        parent_abstract_tag = list(self.root.iter('Abstract'))[0]

        combined_abstract = parse_medline_xml.combine_all_abstract_text_tags(parent_abstract_tag)
        self.assertEqual(correct_abstract_start, combined_abstract[:50])
        self.assertEqual(correct_abstract_end, combined_abstract[-50:])

    def test_abstract_info_parsed_correctly(self):

        abstracttext_tag = list(self.root.iter('AbstractText'))[0]
        d = parse_medline_xml.get_abstract_parent_info(abstracttext_tag)
        correct_title = '[Low level auditory skills compared to writing ski'
        correct_pmid = str(17687753)

        self.assertEqual(d['title'][:50], correct_title)
        self.assertEqual(d['pmid'], correct_pmid)