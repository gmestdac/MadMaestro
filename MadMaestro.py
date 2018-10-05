import argparse
import os
import io
import numpy
import shutil
import getpass
from decimal import *
from shutil import copy2
from subprocess import call

username=getpass.getuser()
here = os.path.dirname(os.path.realpath(__file__))

queue = here + "/jobQueue/jobqueue.txt"
if not(os.path.isdir(here + '/jobQueue/')):
    os.makedirs(here + '/jobQueue/')

cmsenvtemplateLoc = here + "/templates/cmsenvTemplate.sh"

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

# set nevents and pdf using set commands no need to use separate run cards 
# what is in an entry: tuple((valPair,False,overWrite, keepWorkspace, nEvents, priority))


def collect():
    available = {}
    names = os.listdir(here + '/Data/')
    for name in names:
        oppairs = os.listdir(here + '/Data/'+ name)
        # we want the folder name to be noted even if it is empty 
        available.update({name: {} })
        for oppair in oppairs:
            opp = tuple(oppair.split("_-_"))
            opvalpairs = os.listdir(here + '/Data/'+ name + '/' + oppair + '/scripts/')
            collectedVals = {}
            available[name].update({opp:collectedVals})
            opValpairs = [x[:-4] for x in opvalpairs if x[-3:] == "dat"]
            for opvalpair in opvalpairs:
                c1, c2 = opvalpair[:-4].split("_-_")
                c2= c2.split('_')[0]
                try:
                    inFile = open(here + '/Data/'+ name + '/' + oppair + '/results/' + opvalpair + '.txt')
                    res = inFile.read()
                    xsec, err = (res.split())[:2]
                except: 
                    xsec, err = 0.0 , 0.0
                collectedVals.update( {tuple( (Decimal(c1), Decimal(c2)) ) : tuple( (float(xsec),float(err)) )} )
            available[name].update({opp:collectedVals})
    numpy.savez("available.npz", available=available)

# def submit():
    # TODO make sure you submit with a set runtime 

def updateDirs():
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
        shutil.rmtree(here + '/Data/' + name)
    for name in addNames:
        os.makedirs(here + '/Data/' + name)
    for name in rnames:
        rops, aops = set(rdata[name].keys()), set(adata[name].keys())
        intersect = rops.intersection(aops)
        remOps, addOps = aops - intersect, rops - intersect
        for ops in remOps:
            shutil.rmtree(here +  '/Data/' + name + '/' + ops[0] + '_-_' + ops[1])
        for ops in addOps:
            folName = ops[0] + '_-_' + ops[1]
            os.makedirs(here + '/Data/' + name + '/' + folName + '/logs')
            os.makedirs(here + '/Data/' + name + '/' + folName + '/runs')
            os.makedirs(here + '/Data/' + name + '/' + folName + '/results')
            os.makedirs(here + '/Data/' + name + '/' + folName + '/scripts')
        for ops in rops:
            ropvals, aopvals = set(rdata[name][ops]), set(adata[name][ops])
            intersect = ropvals.intersection(aopvals)
            remOpVals= aopvals - intersect
            for valPair in remOpVals:
                path = here + '/Data/' + name + '/' + ops[0] + '_-_' + ops[1] + '/' 
                dat = path + "scripts/{}_-_{}.dat".format(valPair[0],valPair[1])
                sh = path + "scripts/{}_-_{}_{}_{}_{}_{}.sh".format(valPair[0],valPair[1],ops[0],ops[1],name,username) 
                run = path + "runs/{}_-_{}".format(valPair[0],valPair[1])
                results = path + "results/{}_-_{}.txt".format(valPair[0],valPair[1])
                stderr = path + "logs/{}_-_{}.stderr".format(valPair[0],valPair[1])
                stdout = path + "logs/{}_-_{}.stdout".format(valPair[0],valPair[1])
                silentrm(dat,sh,run,results,stderr,stdout)



def silentrm(*args):
# removes a files or folders (and all of their contents) if they exists
    for filepath in args:
        try:
            os.remove(filepath)
        except:
            try:
                shutil.rmtree(filepath)
            except: 
                pass




# FIXME need to implement submission through bigsubmission script 

    # jobqueue = open(queue, 'a')
    # call("stop big-submission", shell=True)
    # jobqueue.write("\n############## " + jobName + " runs start here ##################\n")

    # jobqueue.write("\n############## " + jobName + " runs end here ##################\n")         
    # jobqueue.close()
    # call("big-submission " + queue , shell=True)        

# creates all files and folders needed for a single calculation and returns the command to submit it
def order(name, ops, valPair, keepWorkspace, nevents, model, template, restrictLabel):
    path = here + '/Data/' + name + '/' + ops[0] + '_-_' + ops[1] + '/' 
    dat = path + "scripts/{}_-_{}.dat".format(valPair[0],valPair[1])
    sh = path + "scripts/{}_-_{}_{}_{}_{}_{}.sh".format(valPair[0],valPair[1],ops[0],ops[1],name,username) 
    run = path + "runs/{}_-_{}".format(valPair[0],valPair[1])
    res = run + "/SubProcesses/results.dat".format(valPair[0],valPair[1])
    results = path + "results/{}_-_{}.txt".format(valPair[0],valPair[1])
    stderr = path + "logs/{}_-_{}.stderr".format(valPair[0],valPair[1])
    stdout = path + "logs/{}_-_{}.stdout".format(valPair[0],valPair[1])
    templateLoc = here + '/templates/' + template 

    # always remove files first, but usually they don't exist. Ordering=overwiting!
    silentrm(dat,sh,run,res,stderr,stdout)

    # writing the shell script to be sent to the grid
    template = open(templateLoc,'r')
    indata = template.read()
    template.close()
    outdata = indata.replace("IMPORTMODELRESTRICT","import model " + model + "_UFO-" + restrictLabel + "_" + ops[0] +"_" + ops[1])

    scriptFile = open(dat,'w')
    scriptFile.write(outdata)
    scriptFile.write("\noutput " + run + "\nlaunch " + run + "\ndone\nset " + ops[0] + " " + str(valPair[0]) + "\nset " + ops[1] + " " + str(valPair[1]) + "\n")   
    # TODO make choosing the pdf set more convenient
    scriptFile.write("set pdlabel lhapdf"+ "\nset lhaid 263000"+ "\nset nevents " + str(nevents))
    scriptFile.close()

    copy2(cmsenvtemplateLoc, sh)
    runFile = open(sh, 'a')
    runFile.write(here + "/MG5_aMC_v2_6_0/bin/mg5_aMC " + dat + "\nwait\n")    
    runFile.write("cp -fr " + res + " " + results + "\nwait\n")
    if not(keepWorkspace):
        runFile.write("rm -rf " + run )    
    runFile.close()
    return "qsub -q localgrid -o " + stdout + " -e " + stderr + " " + sh + "\n"

    
# code below is for teting purposes
updateDirs()
order('heltest', ("cuB","cuW"), (Decimal('0.4443'),Decimal('0.2211')), False, 15000, 'HEL', 'testtemplate.dat', 'A')
order('heltest', ("cuB","cuW"), (Decimal('0.5000'),Decimal('-0.2599')), False, 15000, 'HEL', 'testtemplate.dat', 'A')