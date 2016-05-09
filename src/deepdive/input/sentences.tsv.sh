#!/bin/bash

# generates sentence loader scripts
# (run in parallel by deepdive framework)

MINCHUNK=0
MAXCHUNK=10

mkdir -p udf/sentence_import

for i in `seq $MINCHUNK $MAXCHUNK`; do
    echo udf/load_sentences.py $i $MAXCHUNK > udf/sentence_import/"s-"$i".tsv.sh"
done

chmod +x udf/sentence_import/s-*.tsv.sh
