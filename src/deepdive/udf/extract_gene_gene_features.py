#!/usr/bin/env python3
from deepdive import *
import ddlib

@tsv_extractor
@returns(lambda
        g1_id   = "text",
        g2_id   = "text",
        feature = "text",
    :[])
def extract(
        g1_id          = "text",
        g2_id          = "text",
        g1_begin_index = "int",
        g1_end_index   = "int",
        g2_begin_index = "int",
        g2_end_index   = "int",
        doc_id         = "text",
        sent_index     = "int",
        tokens         = "text[]",
        lemmas         = "text[]",
        pos_tags       = "text[]",
        ner_tags       = "text[]",
        dep_types      = "text[]",
        dep_parents    = "int[]",
    ):
    """
    Uses DDLIB to generate features for the spouse relation.
    """
    # Create a DDLIB sentence object, which is just a list of DDLIB Word objects
    sent = []
    for i,t in enumerate(tokens):
        sent.append(ddlib.Word(
            begin_char_offset=None,
            end_char_offset=None,
            word=t,
            lemma=lemmas[i],
            pos=pos_tags[i],
            ner=ner_tags[i],
            dep_par=dep_parents[i] - 1,  # Note that as stored from CoreNLP 0 is ROOT, but for DDLIB -1 is ROOT
            dep_label=dep_types[i]))

    # Create DDLIB Spans for the two person mentions
    g1_span = ddlib.Span(begin_word_id=g1_begin_index, length=(g1_end_index-g1_begin_index+1))
    g2_span = ddlib.Span(begin_word_id=g2_begin_index, length=(g2_end_index-g2_begin_index+1))

    # Generate the generic features using DDLIB
    for feature in ddlib.get_generic_features_relation(sent, g1_span, g2_span):
        yield [g1_id, g2_id, feature]
