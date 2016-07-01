#!/bin/bash

CWD=`pwd`
cd $HOME/local/lib
mv python pythonold
ln -s $CWD"/ddlib/python" .
cd $CWD
