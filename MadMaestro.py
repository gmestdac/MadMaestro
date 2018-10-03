import argparse
import os
import io
import numpy


def collect():
    available = {}
    names = os.listdir('Data/')
    for name in names:
        # print(names)
        oppairs = os.listdir('Data/'+ name)
        # print(oppairs)
        for oppair in oppairs:
            opp = tuple(oppair.split("_-_"))
            # opp = tuple(filter(None, my_str.split('"_-_"')))
            opvalpairs = os.listdir('Data/'+ name + '/' + oppair + '/results/')
            collectedVals = {}
            for opvalpair in opvalpairs:
                # print(opvalpair)
                c1, c2 = opvalpair[:-4].split("_-_")
                # opvp = tuple(filter(None, opvalpair[:-4].split('"_-_"')))
                inFile = open('Data/'+ name + '/' + oppair + '/results/' + opvalpair)
                res = inFile.read()
                xsec, err = (res.split())[:2]
                collectedVals.update( {tuple( (float(c1), float(c2)) ) : tuple( (float(xsec),float(err)) )} )
                # print(collectedVals)
            available.update({name: {opp:collectedVals} })
    print(available)
    numpy.savez("available.npz", available=available)
collect()

# def submit():
