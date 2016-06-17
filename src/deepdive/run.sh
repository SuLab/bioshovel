#!/bin/bash

export CURRENT_DD_APP=`pwd`
MINCHUNK=`cat bioshovel_config.json | deepdive env jq -r '.min_chunk'`
MAXCHUNK=`cat bioshovel_config.json | deepdive env jq -r '.max_chunk'`

deepdive compile

# load articles
deepdive do articles
input/articles.tsv.sh $MINCHUNK $MAXCHUNK
deepdive load articles udf/article_import/a-*.tsv.sh

# load sentences
deepdive do sentences
input/sentences.tsv.sh $MINCHUNK $MAXCHUNK
deepdive load sentences udf/sentence_import/s-*.tsv.sh

# load biothing_tokens
deepdive do biothing_token
input/biothing_token.tsv.sh $MINCHUNK $MAXCHUNK
deepdive load biothing_token udf/biothing_import/b-*.tsv.sh

# create corenlp_token (from sentences table)
deepdive do corenlp_token

# create mention table
deepdive do mention

# create chemical_disease_candidate table
deepdive do chemical_disease_candidate