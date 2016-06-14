#!/usr/bin/env python3

from collections import defaultdict

import sys

class PubtatorParser(object):
    
    def __init__(self, file_path):
        with open(file_path) as f:
            # save entire file, but remove empty lines
            self.file_lines = [line for line in f.readlines() if line.rstrip('\n')]

        # this will be an empty list if no NER information is present:
        self.ner_lines = self.file_lines[2:]

        # filter out CID (Biocreative gold standard) lines
        self.cid_lines = [line for line in self.ner_lines if line.split('\t')[1] == 'CID']
        self.ner_lines = [line for line in self.ner_lines if line.split('\t')[1] != 'CID']

        self.sentence_ner = defaultdict(list)

    def parse_ner(self, sentences):

        ''' sentence_offsets is a list of (start_pos, end_pos) tuples
            with len equal to the number of sentences parsed by CoreNLP

            (start_pos, end_pos) will be integers that correspond to document-level
            character positions
        '''

        sentence_offsets = [(sent['tokens'][0]['characterOffsetBegin'], sent['tokens'][-1]['characterOffsetEnd']) for sent in sentences]

        # self.sentence_ner is a defaultdict with len <= len(sentences)
        #
        # each position in self.sentence_ner contains a list that only has
        # values if there are PubTator NER tags for that sentence
        #
        # e.g.,
        # self.sentence_ner[2] is equal to a list of the unparsed PubTator NER lines
        # corresponding to sentence 2 (may be an empty list if no NER matches)

        # for line in self.ner_lines:
        #     line_split = line.split('\t')
        #     start, end = int(line_split[1]), int(line_split[2])
        #     for sent_num, sent_range in enumerate(sentence_offsets):
        #         if start >= sent_range[0] and end < sent_range[1]:
        #             self.sentence_ner[sent_num].append(line)
        #             break

        for line in self.ner_lines:
            for sent_num, sent_range in enumerate(sentence_offsets):
                biothing = BioNERTag(sent_num, line)
                start, end = biothing.corenlp_offsets
                if start >= sent_range[0] and end < sent_range[1]:
                    self.sentence_ner[sent_num].append(biothing)
                    break

    @property
    def cid_ground_truth_ids(self):

        ''' Returns a list of tuples generated from any given relations
            specified by self.cid_lines

            Tuples will have the form:
            (chem_MESH_id, disease_MESH_id)
        '''

        cid_tuples = []
        for line in self.cid_lines:
            line_split = line.split('\t')
            cid_tuples.append((line_split[2], line_split[3].rstrip('\n')))

        return cid_tuples

class BioNERTag(object):

    def __init__(self, sent_index, line):

        # store the sentence in which this tag was found...
        self.sent_index = sent_index

        self.line = line

        line_split = line.rstrip('\n').split('\t')
        # self.doc_id, self.start_char, self.end_char, self.token, self.ner_type, self.concept_id = line_split

        types = [int, int, int, str, str, str]
        self.doc_id, self.start_char, self.end_char, self.token, self.ner_type, self.concept_id = [t(v) for t, v in zip(types, line_split)]

        self.ner_type = self.ner_type.upper()

        # convert self.concept_id to a set of MESH IDs (will often have len 1)
        if '|' in self.concept_id:
            self.concept_id = set(self.concept_id.split('|'))
        else:
            self.concept_id = set([self.concept_id])

        if sent_index > 0:
            self.start_char_corenlp = self.start_char + 1
            self.end_char_corenlp = self.end_char + 1
        else:
            self.start_char_corenlp = self.start_char
            self.end_char_corenlp = self.end_char

        self.matched_corenlp_token = False

    @property
    def corenlp_offsets(self):
        return (self.start_char_corenlp, self.end_char_corenlp)