#!/bin/bash

# generates article loader scripts
# (run in parallel by deepdive framework)

MINCHUNK=$1
MAXCHUNK=$2
ARTICLE_DIR="udf/article_import"
mkdir -p $ARTICLE_DIR

for i in `seq $MINCHUNK $MAXCHUNK`; do
    echo udf/load_articles.py $i $MAXCHUNK > $ARTICLE_DIR"/a-"$i".tsv.sh"
done

chmod +x $ARTICLE_DIR/a-*.tsv.sh