#!/bin/bash

# generates biothing_token loader scripts
# (run in parallel by deepdive framework)

MINCHUNK=$1
MAXCHUNK=$2
BIOTHING_DIR="udf/biothing_import"
mkdir -p $BIOTHING_DIR

for i in `seq $MINCHUNK $MAXCHUNK`; do
    echo udf/load_biothing_tokens.py $i $MAXCHUNK > $BIOTHING_DIR"/b-"$i".tsv.sh"
done

chmod +x $BIOTHING_DIR/b-*.tsv.sh
