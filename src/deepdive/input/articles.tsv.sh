#!/bin/bash

# a temporary shim until DeepDive supports running 'articles.tsv.*' scripts
exec "${0%.sh}.py" "$@"
