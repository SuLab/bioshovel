# `bioshovel.preprocess`

*for preprocessing article data for use with Name-Entity Recognition (NER) tools*

All modules can be run from the **`src`** directory using **`python3 -m preprocess.[module_name] [args]`**

`/`
--
*scripts for preprocessing article data*

**`preprocess.chem_ner`** for performing chemical name-entity recognition on paragraph data in parform format

* Runs [tmChem](http://dx.doi.org/10.1186/1758-2946-7-S1-S3) using a process pool on a single machine
* Requires Perl to be available in `$PATH` (see `cluster/setup_tmchem.sh`)
* Run using `python3 -m preprocess.chem_ner [path_to_paragraph_documents] [output_directory] --tmchem [path/to/tmChem.pl] --logdir [path/to/save/logfile]`

**`preprocess.chem_ner_cluster`** for running preprocess.chem_ner on a PBS cluster

* Takes input file list and subdivides it into chunks, creates symlinks to original files for each chunk, and creates (and optionally submits) a PBS job file to run each chunk
* Works with huge input directory trees and uses minimal RAM, unless using `--resume` argument
* Run `python3 -m preprocess.chem_ner_cluster -h` for help/options

**`preprocess.create_medline_subset`** for creating a subset of medline based on a list of PMIDs read in from a plain text file (one PMID per line)

* Run using `python3 -m preprocess.create_medline_subset -h` to see help/options

**`preprocess.disease_ner`** for performing disease name-entity recognition on paragraph data in parform format

* Runs [DNorm](http://dx.doi.org/10.1093/bioinformatics/btt474) using a process pool on a single machine
* Requires Java to be available in `$PATH` (tested with OpenJDK Java 7 and Oracle Java 8)
* Run using `python3 -m preprocess.disease_ner [path_to_paragraph_documents] [output_directory] --dnorm [path/to/dnorm/ApplyDNorm.sh/directory] --logdir [path/to/save/logfile]`

**`preprocess.gene_ner`**
for performing gene name-entity recognition on parsed paragraph data in parform format.

* Runs [GNormPlus](http://dx.doi.org/10.1155/2015/918710) using a process pool on a single machine
* Requires Perl to be available in `$PATH`
* Run using `python3 -m preprocess.gene_ner [path_to_paragraph_documents] [output_directory] --gnormplus [path/to/GNormPlus.pl] --logdir [path/to/save/logfile]`

**`preprocess.parse_elife_xml`**
parses [eLife](http://elifesciences.org) articles in XML format from an input directory.

* Extracts a [DOI](https://en.wikipedia.org/wiki/Digital_object_identifier), executive summary paragraphs, abstract paragraph, and body paragraphs while removing all figure and journal citations.
* Run using `python3 -m preprocess.parse_elife_xml [xml_directory]`

**`preprocess.parse_medline_xml`**
parses article abstracts out from MEDLINE XML (and optionally .xml.gz) files. Run using `python3 -m preprocess.parse_medline_xml -h` to see various options

**`preprocess.pmc_prettyprint`**
creates a pretty-printed version of the PubMed Central (or other) XML-based corpus alongside original corpus directory. Run using `python3 -m preprocess.pmc_prettyprint [pmc_xml_directory]`

**`preprocess.prep_corenlp`**
prepares a corpus in parsed/paragraph format for processing with Stanford CoreNLP. 

* For use on a PBS cluster.
* Run `python3 -m preprocess.prep_corenlp -h` for help and options
* Can be run using: `python3 -m preprocess.prep_corenlp [path/to/paragraphs] [output/directory] --corenlp [path/to/coreNLP/installation] --submit`

**`preprocess.reformat`**
functions for reformatting article data to/from various file formats

**`preprocess.util`**
general utility/helper functions for file handling, logging, etc.


`cluster/`
--
*functions and scripts for running tools on a [PBS](https://en.wikipedia.org/wiki/Portable_Batch_System) cluster*

**`preprocess.cluster.util`** utility functions for running on a PBS cluster (such as a wrapper for the job submission command `qsub`)

`setup/`
---
*for set up of local NER tools*

**`setup/setup_tmchem.sh`**
bash script for setting up [tmChem](http://dx.doi.org/10.1186/1758-2946-7-S1-S3) locally

`tests/`
---
*unit tests for `preprocess` package*

**`preprocess.tests.elife_sample_article`**
a sample eLife XML article that is used for eLife parser unit tests

**`preprocess.tests.medline_sample_xml`**
a sample MEDLINE XML abstract that is used for MEDLINE parser unit tests

**`preprocess.tests.test_elife_preprocess`**
unit tests for eLife XML parser functions

**`preprocess.tests.test_medline_preprocess`**
unit tests for MEDLINE XML parser functions

**`preprocess.tests.test_ner`**
unit tests for various `preprocess` functions, including `preprocess.util`