#!/bin/bash

export CURRENT_DD_APP=`pwd`
MINCHUNK=0
MAXCHUNK=0

deepdive compile

# load articles
deepdive do articles
input/articles.tsv.sh $MINCHUNK $MAXCHUNK
deepdive load articles udf/article_import/a-*.tsv.sh

# load sentences
deepdive do sentences
input/sentences.tsv.sh $MINCHUNK $MAXCHUNK
deepdive load sentences udf/sentence_import/s-*.tsv.sh