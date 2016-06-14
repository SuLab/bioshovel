#!/bin/bash

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