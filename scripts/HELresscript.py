# loads a template restrict file and produces one for every operator and every pair of operators
# using restrict files should speed up calculation see https://cp3.irmp.ucl.ac.be/projects/madgraph/wiki/Models/USERMOD
import io
import os
import argparse

argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('-label', action='store', default='A', help="Label for this set (use a letter, A is the default set)")
argParser.add_argument('-template', action='store',         default='restrict_no_b_massHELA.dat', help="Template for set, default is restrict_no_b_massHELA.dat")
args = argParser.parse_args()

template = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'templates/' + args.template))

with open(template, 'r') as file:
    content = file.readlines()

# operators = ["cH","cT","c6","cu","cd","cl","cWW","cB","cHW","cHB","cA","cG","cHQ","cpHQ","cHu","cHd","cHud","cHL","cpHL","cHe","cuB","cuW","cuG","cdB","cdW","cdG","clB","clW","c3W","c3G","c2W","c2B","c2G","tcHW","tcHB","tcG","tcA","tc3W","tc3G"]
# operator values are on lines 82 through 120 in the template
for i in range(81, 120):
    for j in range(81, 120):
        edited = content[:]
        # values need to be different or the paraneters will be merged
        edited[i] = edited[i].replace("0.000000e+00", "0.100000e+00")
        edited[j] = edited[j].replace("0.000000e+00", "0.200000e+00")
        # figure out which operators we are setting to a nonzero value
        c1 = edited[i].split()[3]
        c2 = edited[j].split()[3]
        # I add an extra label (standard A) so in case other sets of restrics files are ever needed
        # always sort operator labels alphabetically for consistency
        outPath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'MG5_aMC_v2_6_3_2/models/HEL_UFO/restrict_' + args.label + "_" + sorted([c1,c2])[0] + "_" + sorted([c1,c2])[1] + ".dat" ))
        with open(outPath, 'w') as file:
            file.writelines( edited )

