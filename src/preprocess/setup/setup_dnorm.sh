#!/bin/bash

# This script configures a blank Amazon Web Service EC2 instance with DNorm
# DNorm is installed into bioshovel/tools

# This script assumes that the Amazon Machine Image used is:
# Ubuntu Server 14.04 LTS (HVM, 64 bit), SSD Volume Type - ami-fce3c696

echo "Installing dependencies"
sudo apt-add-repository -y ppa:webupd8team/java
sudo apt-get update
sudo apt-get install -y build-essential git oracle-java8-installer

echo "Cloning bioshovel repository"
git clone https://github.com/SuLab/bioshovel.git

echo "Creating tools directory"
cd bioshovel
git branch preprocess
git checkout preprocess
git pull origin preprocess

mkdir tools
cd tools

echo "Download Ab3P"
wget ftp://ftp.ncbi.nlm.nih.gov/pub/wilbur/Ab3P-v1.5.tar.gz
tar -xvf Ab3P-v1.5.tar.gz
rm Ab3P-v1.5.tar.gz

echo "Build Ab3P"
cd Ab3P-v1.5
make
make test
cd ..

echo "Downloading DNorm"
wget http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/tmTools/download/DNorm/DNorm-0.0.7.tgz
tar -xvf DNorm-0.0.7.tgz
rm DNorm-0.0.7.tgz

echo "Test DNorm"
cd DNorm-0.0.7
./EvalDNorm.sh data/CTD_diseases-2015-06-04.tsv data/BC5CDR/abbreviations.tsv config/banner_BC5CDR_UMLS2013AA_SAMPLE.xml output/simmatrix_BC5CDR_e4_TRAINDEV.bin output/analysis.txt
