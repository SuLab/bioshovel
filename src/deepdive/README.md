# `bioshovel.deepdive`

*a [DeepDive](http://deepdive.stanford.edu) application for "biothing" relation extraction*

Entire pipeline can be run from the base directory using **`./run.sh`**

`/`
--
*for use with DeepDive v0.8*

**`app.ddlog`**

* contains application table schema and data flow written in DDLog

**`bioshovel_config.json`**

* contains instance-specific user-defined parameters for the Bioshovel application

**`db.url`** contains database connection information (PostgreSQL)

**`deepdive.conf`** contains holdout SQL query to define development or test set

**`run.sh`** for running entire Bioshovel/DeepDive pipeline

* Sets necessary environment variables
* Creates database for project
* Requires `deepdive` (v0.8) to be in `$PATH`
* Requires Python3 to be installed and available via `python3` in `$PATH`
* Requires Bioshovel Python dependencies to be installed (see `../../requirements.txt`)
* Requires Python3-compatible `ddlib` to be installed by linking `[user_home]/local/lib/python` to directory `ddlib/python` *(will be unnecessary in a future DeepDive release)*

`ddlib/`
--
*Python3-compatible `ddlib` library*

* see https://github.com/HazyResearch/deepdive/tree/master/ddlib

`input/`
--
*helper scripts to support parallelized data loading via `deepdive load [table] [script]` commands*

**`articles.tsv.sh`**

**`biothing_token.tsv.sh`**

**`sentences.tsv.sh`**

`udf/`
--
*user-defined functions*

**`corenlp_parse.py`**

* Contains Stanford CoreNLP parser class (NLPParser) and methods to return appropriately formatted data for import into PostgreSQL database tables

**`extract_chemical_disease_features.py`**

* Reconciles NER tags for sentence tokens based on CoreNLP assignments and reassignments from PubTator annotation (see `load_biothing_tokens.py` for implementation of token NER matching)
* Generates [generic features](http://deepdive.stanford.edu/gen_feats) using `ddlib`
* See `app.ddlog` for full details on input data format for the `chemical_disease_feature` database table

**`load_articles.py`**

* Loads articles from **.tgz files** into database `articles` table
* Uses data directory specified in `../bioshovel_config.json`
* tar files must have specific names (to match glob expression)
    * `*_{}_combined.tgz` where {} is some chunk number within `$MINCHUNK` and `$MAXCHUNK` (see `../bioshovel_config.json`)
* tar file must have specific directory structure for proper import
    * contents of sample data chunk (archive file) `large_corpus_0_combined.tgz`
        * `input_files/` contains plain text input files used for CoreNLP. These files are typically named by PMID (e.g., `10091617`) or escaped DOI (e.g., `10.1371%2Fjournal.pbio.1002375`). These files are the generated input files from `preprocess.prep_corenlp`
        * `output_files/` contains JSON files that are output from CoreNLP. These files are the output from `preprocess.prep_corenlp` and are named `[input_filename].json` (e.g., `10091617.json`)
        * `pubtator/` contains plain text files in PubTator format. Files are named by PMID or escaped DOI (same as `input_files/*`)
        * `pubtator_cid/` contains plain text files in PubTator format, including *CID* ground truth relations included from the [BioCreative V CDR challenge](http://www.biocreative.org/tasks/biocreative-v/track-3-cdr/)

**`load_sentences.py`**

* loads sentences from **.tgz files** into database `sentences` table
* tar files must have same format as specified for `load_articles.py`

**`load_biothing_tokens.py`**

* loads biothing tokens identified from **.tgz files** into database `biothing_token` table
* tar files must have same format as specified for `load_articles.py`
* CoreNLP tokens are parsed from `[tar_file]/output_files/*` and remapped to 'biothing' NER classes (CHEMICAL, DISEASE, etc.) based on matched PubTator annotation

**`pubtator_parse.py`**

* Contains PubtatorParser and BioNERTag classes for parsing a PubTator file into Python objects

**`util.py`**

* Contains helper functions, including...
    * a print statement `printl` that allows for printing to the DeepDive log via `STDERR` (since `STDOUT` is captured by the DeepDive pipeline)
    * a function to load the config JSON file
    * a function to filter out a subset of files from a tar file based on a string subset of the full file paths (`filter_files_from_tar`)