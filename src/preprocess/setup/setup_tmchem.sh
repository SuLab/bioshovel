#!/bin/bash

# Tong Shu Li
# Last updated: 2016-03-23

# This script configures a blank Amazon Web Service EC2 instance with tmChem
# tmChem is installed into bioshovel/tools

# This script assumes that the Amazon Machine Image used is:
# Ubuntu Server 14.04 LTS (HVM, 64 bit), SSD Volume Type - ami-fce3c696

echo "Link sh command to bash"
sudo rm /bin/sh
sudo ln -s /bin/bash /bin/sh

echo "Updating package repository"
sudo apt-get update

echo "Installing packages"
sudo apt-get install -y unzip build-essential cpanminus git

echo "Installing Perl TokeParser package"
sudo cpanm HTML::TokeParser

echo "Cloning bioshovel repository"
git clone https://github.com/SuLab/bioshovel.git

cd bioshovel

echo "Creating tools directory"
mkdir tools

echo "Downloading tmChem from http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/tmTools/download/tmChem/tmChem.M2.ver02.zip"
wget http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/tmTools/download/tmChem/tmChem.M2.ver02.zip

echo "Unpacking tmChem"
unzip tmChem.M2.ver02.zip -d tools

echo "Renaming tmChem folder"
mv tools/tmChem tools/tmChem.M2.ver02

echo "Removing tmChem zip file"
rm tmChem.M2.ver02.zip

echo "Install tmChem"
cd tools/tmChem.M2.ver02
sh Installation.sh

echo "Done. tmChem installed successfully"
