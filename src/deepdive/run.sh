#!/bin/bash

export CURRENT_DD_APP=`pwd`

deepdive compile

deepdive do articles
#deepdive redo articles

# generate sentence loader scripts
input/sentences.tsv.sh

deepdive do sentences
deepdive load sentences udf/sentence_import/s-*.tsv.sh

deepdive do person_mention

deepdive do chemical_mention

deepdive do disease_mention

deepdive do gene_mention

deepdive do species_mention

deepdive do gene_gene_candidate

deepdive do chemical_disease_candidate

deepdive do chemical_disease_feature

# deepdive do cid_ground_truth
# deepdive load cid_ground_truth udf/load_labeled_data.tsv.sh

deepdive do sentences_training
deepdive load sentences_training udf/load_labeled_data.tsv.sh

deepdive do chemical_mention_training

deepdive do disease_mention_training

deepdive do cid_ground_truth