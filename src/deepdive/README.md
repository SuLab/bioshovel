# `bioshovel.deepdive`

*a DeepDive application for "biothing" relation extraction*

Entire pipeline can be run from the base directory using **`./run.sh`**

`/`
--
*for use with DeepDive v0.8*

**`app.ddlog`**

* contains application table schema and data flow written in DDLog

**`bioshovel_config.json`**

* contains instance-specific user-defined parameters for the Bioshovel application

**`run.sh`** for running entire Bioshovel/DeepDive pipeline

* Sets necessary environment variables
* Requires `deepdive` (v0.8) to be in `$PATH`
* Requires Python3 to be installed and available via `python3` in `$PATH`
* Requires Bioshovel Python dependencies to be installed (see `../../requirements.txt`)
* Requires Python3-compatible `ddlib` to be installed by linking `[user_home]/local/lib/python/ddlib` to directory `ddlib` *(will be unnecessary in a future DeepDive release)*

`input/`
--
*data loader helper scripts*

**`articles.tsv.sh`**

**`biothing_token.tsv.sh`**

**`sentences.tsv.sh`**

`udf/`
--
*user-defined functions*

**`corenlp_parse.py`**

**`extract_chemical_disease_features.py`**

**`load_articles.py`**

**`load_sentences.py`**

**`load_biothing_tokens.py`**

**`pubtator_parse.py`**

**`util.py`**