# this script deploys MadMaestro but increases entropy
# TODO add the CMSSW stuff to install instructions
eval `scram runtime -sh`
cd $CMSSW_BASE/src

git clone https://github.com/gmestdac/MadMaestro.git
cd MadMaestro
location="$(pwd)"
wget https://launchpad.net/mg5amcnlo/2.0/2.6.x/+download/MG5_aMC_v2.6.3.2.tar.gz
tar -xf MG5_aMC_v2.6.3.2.tar.gz
rm MG5_aMC_v2.6.3.2.tar.gz

cd MG5_aMC_v2_6_3_2/models/
# TODO get the modified HEL model in there somehow
wget https://feynrules.irmp.ucl.ac.be/raw-attachment/wiki/dim6top/dim6top_LO_UFO.tar.gz
tar -xf dim6top_LO_UFO.tar.gz
rm dim6top_LO_UFO.tar.gz
cd..
cd.. 
wget http://www.hepforge.org/archive/lhapdf/LHAPDF-6.2.1.tar.gz
tar xf LHAPDF-6.2.1.tar.gz
rm LHAPDF-6.2.1.tar.gz
cd LHAPDF-6.2.1 
echo -n "Installing LHAPDF, good time grab a coffee"
./configure --prefix="$location"/LHAPDF
make
make install
cd ..
rm -rf LHAPDF-6.2.1 