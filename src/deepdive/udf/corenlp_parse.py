#!/usr/bin/env python3

import os
import json
import sys

class NLPParser(object):

    def __init__(self, file_path):
        with open(file_path) as f:
            self._json = json.load(f, strict=False)

        # for now, exclude files with strange XML contents, e.g.,
        #
        # ip-172-30-0-123 output_files> cat ../input_files/10179206
        # The wake-effect--emergency vehicle-related collisions.

        # INTRODUCTION: Emergency medical vehicle collisions (EMVCs) occurring 
        # during initial response and with patient transport have been a 
        # long-standing problem for emergency medical services (EMS) systems. 
        # Experience suggests "wake-effect" collisions occur as a result of an 
        # EMS vehicle's transit, but do not involve the emergency medical 
        # vehicle (EMV). Substantiating the existence and magnitude of 
        # wake-effect collisions may have major implications regarding the 
        # manner of EMV response. HYPOTHESIS: Paramedics will report that 
        # wake-effect collisions do occur and that they occur more frequently 
        # than do EMVCs. METHODS:                 <AbstractText Label="DESIGN" 
        #  v="METHODS">Survey analysis. PARTICIPANTS: Thirty paramedics
        # employed by the Salt Lake City (Utah) Fire Department and 45 
        # paramedics employed by Salt Lake County Fire Department. 
        # Geographic Area: Service area has population of 650,000 and is urban, 
        # suburban, and rural. MEASUREMENTS: The survey consisted of three 
        # open-ended questions concerning years on the job, EMVCs, and 
        # wake-effect collisions. ANALYSIS: The mean value for the number of 
        # EMVCs and wake-effect EMVCs, along with the 0.95 confidence intervals 
        # (0.95 CI) were determined. RESULTS: Seventy-three surveys were 
        # analyzed. Sixty EMVCs and 255 wake-effect collisions were reported. 
        # Overall, the mean value for the number EMVCs per respondent was 0.82 
        # (0.60-1.05) and for wake-effect collisions 3.49 (2.42-4.55). The 
        # mean values for EMVC's for each service were 0.86 (0.50-1.38); 0.80 
        # (0.50-11.0). For wake-effect collisions the mean values were 4.59 
        # (2.83-6.35); and 2.76 (1.46-4.06) respectively. CONCLUSIONS: This 
        # study suggests that the wake-effect collision is real and may occur 
        # with greater frequency than do EMVCs. Significant limitations of this 
        # study are recall bias and misclassification bias. Future studies are 
        # needed to define more precisely wake-effect collision prevalence and 
        # the resulting "cost" in regards to injury and vehicle/property damage.

        # ip-172-30-0-123 output_files> grep -c AbstractText * | cut -f 2 -d ':' | sort | uniq -c
        #   49993 0
        #       1 12
        #       1 18
        #       1 21
        #       3 6
        #       2 9
        # ip-172-30-0-123 output_files> pwd
        # /home/ubuntu/sandip/bioshovel_dd/data/corpus/pubtator_abstracts/subset_1/output_files

        # also exclude "<font" -- see error
        # ERROR:  malformed array literal: "{"Both","of","these","antibodies","belong","to","subclass","IgG","-LRB-","1","-RRB-",",","<font?face="k">","k.","K","-LRB-","d","-RRB-","values","were","7.3","x","10","-LRB-","-8","-RRB-","for","3G8","and","1.1","x","10","-LRB-","-6","-RRB-","for","betaG1","."}"


        if 'AbstractText' in str(self._json) or '<font' in str(self._json):
            self.exclude = True
        else:
            self.exclude = False

        self.doc_id = os.path.basename(file_path).replace('.json', '')
        self.num_sents = len(self._json['sentences'])

    @property
    def sentences(self):
        return self._json.get('sentences', None)
    
    def __iter__(self):
        self.sent_index = 0

        if self.exclude:
            # set index to max so that iteration does not occur
            self.sent_index = self.num_sents

        return self

    def __next__(self):

        self.sent_index += 1
        if self.sent_index >= self.num_sents:
            raise StopIteration

        current_sentence = self.sentences[self.sent_index]

        # return each sentence as a table row (tab-delimited string)

        # TABLE SCHEMA:
        # doc_id         text,
        # sentence_index int,
        # sentence_text  text,
        # tokens         text[],
        # lemmas         text[],
        # pos_tags       text[],
        # ner_tags       text[],
        # doc_offsets    int[],
        # dep_types      text[],
        # dep_tokens     int[]

        doc_id = self.doc_id
        sentence_index = self.sent_index
        sentence_text = self.get_sentence_text(current_sentence).replace('\n', ' ')
        tokens = self.get_sentence_token_key(current_sentence, 'word')
        lemmas = self.get_sentence_token_key(current_sentence, 'lemma')
        pos_tags = self.get_sentence_token_key(current_sentence, 'pos')
        ner_tags = self.get_sentence_token_key(current_sentence, 'ner')
        doc_offsets = self.get_sentence_offsets(current_sentence)
        dep_types = '{text9,text10}'
        dep_tokens = '{3,4,5}'

        data = [doc_id,
                sentence_index,
                sentence_text,
                tokens,
                lemmas,
                pos_tags,
                ner_tags,
                doc_offsets,
                dep_types,
                dep_tokens]

        single_row = '\t'.join([str(item) for item in data])

        return single_row

    @staticmethod
    def get_sentence_token_key(sent, key, join_str=',', prefix='{', suffix='}', surround_quotes=True):
        
        ''' Given a sentence, return sentence.token[key]
            for import into sentences database table
        '''

        value_list = [t[key] for t in sent['tokens']]

        if surround_quotes:
            value_list = ['"{}"'.format(v) for v in value_list]

        return prefix + join_str.join(value_list) + suffix

    @staticmethod
    def get_sentence_text(sent):

        ''' Given a list of sentences, return sentence
            text for import into sentences table
        '''
        # TODO: reconstruct sentence from words using 'after' and 'before' keys
        # so that spacing around punctuation is correct
        
        l = []
        for token in sent['tokens']:
            l.append(token['before']+token['originalText'])

        return ''.join(l)

    @staticmethod
    def get_sentence_offsets(sent, string_output=True):
        
        ''' Given a sentence, return word start positions
            (offsets) for each word relative to the start
            of the document
        '''

        tokens = sent['tokens']
        start_positions = [t['characterOffsetBegin'] for t in tokens]
        if string_output:
            return '{'+','.join([str(pos) for pos in start_positions])+'}'
        else:
            return start_positions

