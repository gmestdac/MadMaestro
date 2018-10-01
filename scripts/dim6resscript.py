
# loads a template restrict file and produces one for every operator and every pair of operators
# using restrict files should speed up calculation see https://cp3.irmp.ucl.ac.be/projects/madgraph/wiki/Models/USERMOD
import io
import os
import argparse

argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('-label', action='store', default='A', help="Label for this set (use a letter, A is the default set)")
argParser.add_argument('-template', action='store',         default='restrict_no_b_massdim6A.dat', help="Template for set, default is restrict_no_b_massdim6A.dat")
args = argParser.parse_args()

template = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'templates/' + args.template))

with open(template, 'r') as file:
    content = file.readlines()

# operator values are on lines 83 through 154 in the template
for i in range(82, 154):
    for j in range(82, 154):
        edited = content[:]
        # values need to be different or the paraneters will be merged
        edited[i] = edited[i].replace("0.000000e+00", "0.100000e+00")
        edited[j] = edited[j].replace("0.000000e+00", "0.200000e+00")
        # figure out which operators we are setting to a nonzero value
        c1 = edited[i].split()[3]
        c2 = edited[j].split()[3]
        # I add an extra label (standard A) so in case other sets of restrics files are ever needed
        # always sort operator labels alphabetically for consistency
        outPath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'MG5_aMC_v2_6_3_2/models/dim6top_LO_UFO/restrict_' + args.label + "_" + sorted([c1,c2])[0] + "_" + sorted([c1,c2])[1] + ".dat" ))
        with open(outPath, 'w') as file:
            file.writelines( edited )

