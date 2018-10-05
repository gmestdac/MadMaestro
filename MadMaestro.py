import argparse
import os
import io
import numpy
import shutil



# Make list of things to be submitted
# - not in available, but in requested
# - available but overwrite is set
# get the bigsubmission list 
# get the list of running jobs
# bash qstat -f  (for full info) |grep username?  only lines with username would be printed... (whoami in bash but python command available to check)
# maybe without -f if filenames are'nt too long, probably will be though
# BETTER: qstat -f | grep Job_Name       AND inlude username in sh scipt filename to prevent conflicts 
# filter out

# more practically:  list requested, remove remove available if not to be overwitten


def collect():
    available = {}
    names = os.listdir('Data/')
    for name in names:
        oppairs = os.listdir('Data/'+ name)
        # we want the folder name to be noted even if it is empty 
        available.update({name: {} })
        for oppair in oppairs:
            opp = tuple(oppair.split("_-_"))
            opvalpairs = os.listdir('Data/'+ name + '/' + oppair + '/results/')
            collectedVals = {}
            available.update({name: {opp:collectedVals} })
            for opvalpair in opvalpairs:
                c1, c2 = opvalpair[:-4].split("_-_")
                inFile = open('Data/'+ name + '/' + oppair + '/results/' + opvalpair)
                res = inFile.read()
                xsec, err = (res.split())[:2]
                collectedVals.update( {tuple( (float(c1), float(c2)) ) : tuple( (float(xsec),float(err)) )} )
            available.update({name: {opp:collectedVals} })
    numpy.savez("available.npz", available=available)

# def submit():
    # TODO make sure you submit with a set runtime 

def compare():
    collect()
    try:
        rdata = numpy.load("requested.npz")["data"].item()
        adata = numpy.load("available.npz")["available"].item()
    except:
        print("Nothing requested")
        return
    rnames, anames = set(rdata.keys()), set(adata.keys())
    intersect = rnames.intersection(anames)
    remNames, addNames = anames - intersect, rnames - intersect
    for name in remNames:
        shutil.rmtree('./Data/' + name)
    for name in addNames:
        os.makedirs('./Data/' + name)
    collect()  
    # TODO not sure what will be faster, removing from available while running, or rerunning collect, might change in future
    for name in rnames:
        rops, aops = set(rdata[name].keys()), set(adata[name].keys())
        intersect = rops.intersection(aops)
        remOps, addOps = aops - intersect, rops - intersect
        for ops in remOps:
            shutil.rmtree('./Data/' + name + '/' + ops[0] + '_-_' + ops[1])
        for ops in addOps:
            folName = ops[0] + '_-_' + ops[1]
            os.makedirs('./Data/' + name + '/' + folName + '/logs')
            os.makedirs('./Data/' + name + '/' + folName + '/runs')
            os.makedirs('./Data/' + name + '/' + folName + '/results')
            os.makedirs('./Data/' + name + '/' + folName + '/scripts')
compare()