# BioShovel

*For text mining of biological research articles using [DeepDive](http://deepdive.stanford.edu)*

**Tong Shu Li** and **Sandip Chatterjee** of the [Su Lab](http://sulab.org)

[![Build Status](https://travis-ci.org/SuLab/bioshovel.svg?branch=dev)](https://travis-ci.org/SuLab/bioshovel)

## Getting Started

### Requirements
* Python 3.4+
* Java 1.8 for various NER/NLP annotators
* PBS/Torque cluster for cluster workflows
* Python package dependencies in `requirements.txt`
    * `lxml` may require external `libxml2` installation (using a tool like `apt-get`)

### Ensuring `pip3` and `libxml2` are installed

* On Ubuntu (14.04), run `sudo apt-get install -y python3-pip`
* Install `lxml` dependencies using: `sudo apt-get install -y libxml2 libxml2-dev libxslt1-dev lib32z1-dev`

### Installing Python dependencies

* Clone the repo and `cd bioshovel`
* Create a virtualenv: `$ python3 -m venv venv`
* Activate virtualenv: `$ source venv/bin/activate`
* Install dependencies: `(venv) $ pip install -r requirements.txt`

### Run BioShovel modules

* Modules should be run from the `src` directory
* Use `(venv) $ python3 -m [package_name].[module_name] [args]`
* See [preprocess](src/preprocess) and [downloaders](src/downloaders) packages for more information

### Running Unit Tests

* Tests should be run from the `src` directory
* Run test discovery using `python3 -m unittest`