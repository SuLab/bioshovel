#!/usr/bin/env python3
from deepdive import *
import ddlib

@tsv_extractor
@returns(lambda
        chemical_id   = "text",
        disease_id   = "text",
        feature = "text",
    :[])
def extract(
        chemical_id          = "text",
        disease_id           = "text",
        chemical_begin_index = "int",
        chemical_end_index   = "int",
        disease_begin_index  = "int",
        disease_end_index    = "int",
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
    chemical_span = ddlib.Span(begin_word_id=chemical_begin_index, length=(chemical_end_index-chemical_begin_index+1))
    disease_span = ddlib.Span(begin_word_id=disease_begin_index, length=(disease_end_index-disease_begin_index+1))

    # Generate the generic features using DDLIB
    for feature in ddlib.get_generic_features_relation(sent, chemical_span, disease_span):
        yield [chemical_id, disease_id, feature]
