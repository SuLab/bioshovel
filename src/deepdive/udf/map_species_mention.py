#!/usr/bin/env python3
from deepdive import *

@tsv_extractor
@returns(lambda
        mention_id       = "text",
        mention_text     = "text",
        doc_id           = "text",
        sentence_index   = "int",
        begin_index      = "int",
        end_index        = "int",
    :[])
def extract(
        doc_id         = "text",
        sentence_index = "int",
        tokens         = "text[]",
        ner_tags       = "text[]",
    ):
    """
    Finds phrases that are continuous words tagged with SPECIES.
    """
    num_tokens = len(ner_tags)
    # find all first indexes of series of tokens tagged as SPECIES
    first_indexes = (i for i in range(num_tokens) if ner_tags[i] == "SPECIES" and (i == 0 or ner_tags[i-1] != "SPECIES"))
    for begin_index in first_indexes:
        # find the end of the SPECIES phrase (consecutive tokens tagged as SPECIES)
        end_index = begin_index + 1
        while end_index < num_tokens and ner_tags[end_index] == "SPECIES":
            end_index += 1
        end_index -= 1
        # generate a mention identifier
        mention_id = "%s_%d_%d_%d" % (doc_id, sentence_index, begin_index, end_index)
        mention_text = " ".join(map(lambda i: tokens[i], range(begin_index, end_index + 1)))
        # Output a tuple for each SPECIES phrase
        yield [
            mention_id,
            mention_text,
            doc_id,
            sentence_index,
            begin_index,
            end_index,
        ]
