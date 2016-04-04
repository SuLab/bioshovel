# `bioshovel.tests`

*for preprocessing article data for use with Name-Entity Recognition (NER) tools*

Run unit tests from **`src`** directory by running:

```bash
$ python3 -m unittest
```

`/`
---
*unit tests*

**`tests.elife_sample_article`**
a sample eLife XML article that is used for eLife parser unit tests

**`tests.medline_sample_xml`**
a sample MEDLINE XML abstract that is used for MEDLINE parser unit tests

**`tests.test_elife_preprocess`**
unit tests for eLife XML parser functions

**`tests.test_medline_preprocess`**
unit tests for MEDLINE XML parser functions

**`tests.test_ner`**
unit tests for various `preprocess` functions, including `preprocess.util`