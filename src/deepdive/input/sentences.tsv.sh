#!/bin/bash

# generates sentence loader scripts
# (run in parallel by deepdive framework)

MINCHUNK=$1
MAXCHUNK=$2
SENTENCE_DIR="udf/sentence_import"
mkdir -p udf/sentence_import

for i in `seq $MINCHUNK $MAXCHUNK`; do
    echo udf/load_sentences.py $i $MAXCHUNK > $SENTENCE_DIR"/s-"$i".tsv.sh"
done

chmod +x $SENTENCE_DIR/s-*.tsv.sh
