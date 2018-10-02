#!/bin/bash

# this script deploys MadMaestro but increases entropy
# TODO add the CMSSW stuff to install instructions

# eval `scram runtime -sh`
# cd $CMSSW_BASE/src

location="$(pwd)"
wget https://launchpad.net/mg5amcnlo/2.0/2.6.x/+download/MG5_aMC_v2.6.3.2.tar.gz
tar -xf MG5_aMC_v2.6.3.2.tar.gz
rm MG5_aMC_v2.6.3.2.tar.gz

cd MG5_aMC_v2_6_3_2/models/
wget https://feynrules.irmp.ucl.ac.be/raw-attachment/wiki/dim6top/dim6top_LO_UFO.tar.gz
tar -xf dim6top_LO_UFO.tar.gz
rm dim6top_LO_UFO.tar.gz
cd..
cd.. 
tar -xf ./templates/modHEL_UFO.tar.gz -C ./MG5_aMC_v2_6_3_2/models/
wget http://www.hepforge.org/archive/lhapdf/LHAPDF-6.2.1.tar.gz
tar xf LHAPDF-6.2.1.tar.gz
rm LHAPDF-6.2.1.tar.gz
cd LHAPDF-6.2.1 
echo -e '\033[1m\n\nInstalling LHAPDF, this a good time grab a coffee \n\n\033[0m'
./configure --prefix="$location"/LHAPDF
make
make install
cd ..
rm -rf LHAPDF-6.2.1 
# 
lhapdfpath=$(readlink -e ./LHAPDF/bin/lhapdf-config) 
sed "s|TOBEREPLACEDBYSCRIPT| lhapdf = $lhapdfpath|g" ./templates/mg5_configuration.txt > ./MG5_aMC_v2_6_3_2/input/mg5_configuration.txt
# making the standard set restrict files
cd scripts
python HELresscript.py
python dim6resscript.py
cd ..