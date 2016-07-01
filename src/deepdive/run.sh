#!/bin/bash

# check if `deepdive` is in $PATH
if ! type "deepdive" 2> /dev/null 1>&2; then 
    echo "DeepDive not installed or not in \$PATH";
    if type $HOME/local/bin/deepdive 2> /dev/null 1>&2; then
        echo "Try adding the following to ~/.bashrc and restarting shell:";
        echo "PATH=$HOME/local/bin:\$PATH; export PATH";
    fi
    echo "Exiting...";
    exit 1;
fi

# install ddlib for python3 (from local repo version)
./install_ddlib_py3.sh

export CURRENT_DD_APP=`pwd`
MINCHUNK=`cat bioshovel_config.json | deepdive env jq -r '.min_chunk'`
MAXCHUNK=`cat bioshovel_config.json | deepdive env jq -r '.max_chunk'`
DBNAME=`cat bioshovel_config.json | deepdive env jq -r '.database_name'`
createdb $DBNAME

echo "postgresql://ubuntu@localhost:5432/$DBNAME" > db.url

# pull out CID ground truth relations
TRAINTGZ=`cat bioshovel_config.json | deepdive env jq -r '.training_data_tgz'`
cd `dirname $TRAINTGZ`
tar -xf `basename $TRAINTGZ`
# TODO: fix the following command (the `cat` portion of the pipeline) to work 
# with any training data directory name... not just hardcoded name
cat biocreative_cdr_training/pubtator_cid/* | grep -P '\tCID\t' | awk -v OFS='\t' '{ print $3, $4, $2 }' > /tmp/chemical_disease_gt.tsv
cd $CURRENT_DD_APP
mv /tmp/chemical_disease_gt.tsv input/

# don't open editor for plan for each each `deepdive do`
export DEEPDIVE_PLAN_EDIT=false

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

# create chemical_disease_feature table and extract features using UDF
deepdive do chemical_disease_feature

# load CID ground truth relations into data table
deepdive do chemical_disease_gt

deepdive do probabilities

deepdive do calibration-plots
