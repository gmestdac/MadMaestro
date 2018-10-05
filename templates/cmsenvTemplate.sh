pwd=$PWD
source $VO_CMS_SW_DIR/cmsset_default.sh                          # make scram available                                                                                                                                                             
cd /user/$USER/CMSSW_9_4_3/src/                          # your local CMSSW release                                                                                                                                                         
eval `scram runtime -sh`                                         # don't use cmsenv, won't work on batch                                                                                                                                            
cd $pwd

