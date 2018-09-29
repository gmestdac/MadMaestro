
import argparse
import os
import io
import numpy
import pprint 

argParser = argparse.ArgumentParser(description = "Argument parser for MadMaesto. get help for any of the functions below by typing its name before --help")
subparsers = argParser.add_subparsers(dest='subparser_name')

add_Parser = subparsers.add_parser('add')
remove_Parser = subparsers.add_parser('remove')
addName_Parser = subparsers.add_parser('addName')
removeName_Parser = subparsers.add_parser('removeName')
listNames_Parser = subparsers.add_parser('listNames')
list_Parser = subparsers.add_parser('list')


# argument parser for adding datapoints
add_Parser.add_argument('name',                     action='store',                                         help="Name op the dataset to add requests to")
add_Parser.add_argument('-c','--coeff',             action='append',        nargs=4,                        help="Scan over a coefficient, needs 4 arguments: coefficient, begin, end, number of values. Add this multiple times to perform 2D scans pairs of all speciefied operators. The SM case will always be included.", metavar=('COEFF', 'BEGIN', 'END', 'NUMBER'))
add_Parser.add_argument('-n','--nEvents',           action='store',         default = 10000,    type=int,   help="Number of Events" )
add_Parser.add_argument('-o','--overwrite',         action='store_true',    default=False,                  help="Overwrite exisiting results, deletion of existing files and results is done when requesting")
add_Parser.add_argument('--keepWorkspace',          action='store_true',    default=False,                  help="keep the MadGraph event folder?")
add_Parser.add_argument('-s',"--specific",          action="append",        nargs=4,                        help="Define specific coefficient values instead of scanning. Can be specified multiple times. Format: c1 c2 c1value c2value. If c1=c2 adds c1value 1 and 2 to the corresponding 1D data")

# argument parser for removing datapoints
remove_Parser.add_argument('name',                  action='store',                                         help="Name op the dataset to add requests to")
remove_Parser.add_argument('-c','--coeff',          action='append',                                        help= "remove data associated with this coefficient, specifying mutiple operators (-c in front of each) removes data associated with each possible coefficient pair")
remove_Parser.add_argument('-s',"--specific",       action="append",        nargs=4,                        help="Remove only data corresponding to specific coefficient values. Can be specified multiple times. Format: c1 c2 c1value c2value")

# argument parser for adding a dataset name
addName_Parser.add_argument('name',                 action='store',                                         help="Name to associate with this dataset")
addName_Parser.add_argument('model',         action='store',         choices=['HEL_UFO', 'dim6top_LO', 'dim6top_LO_v2'], help="Which madgraph model to use?")
addName_Parser.add_argument('procTemplate',         action='store',                                         help="Specify the process template card")
addName_Parser.add_argument('restrictSet',          action='store',                                         help="Specify restrict card label")

# argument parser for removing datasets
removeName_Parser.add_argument('name',              action='store',         nargs='+',                        help="Provide any number of names to be removed")

# argument parser for listing Names and associated info 
listNames_Parser.add_argument('--name','-n',        action='store',         default="listall", help="Get info on a specific name instead if listing them all")

list_Parser.add_argument('name',               action='store',         default="listall", help="Get info on a specific name instead if listing them all")
list_Parser.add_argument('name',               action='store',         default="listall", help="Get info on a specific coefficient (pair)")

args = argParser.parse_args()

# TODO list available options 
# TODO maak volgorde consistent door te sorten  AAN BEGIN VAN PROGRAMMA
# TODO converteer naar floats bij opslaan vor gemak later


# A name corresponds to a specific process, model, and set of restrict cards (might be needed for nobmass and bmass scenarios)
def addName(name, model, procTemplate, restrictSet):
# loading a dictionary of dictionaries saved using savez is a bit weird
    try:
        index = numpy.load("requested.npz")["index"].item()
        data = numpy.load("requested.npz")["data"].item()
    except:
        index = {}
        data = {}
    if not ( os.path.isfile("templates/" + procTemplate)):  
        print("process card template is missing")
        return    
#   TODO might want to check if the restrict set label is legit as well
    index.update({name: [model, procTemplate, restrictSet]})
    numpy.savez("requested.npz", index=index, data=data)


def addRequests(name, op1, op2, opVals ):
    try:
        index = numpy.load("requested.npz")["index"].item()
        data = numpy.load("requested.npz")["data"].item()
    except:
        index = {}
        data = {}
    finally:
        # NOTE in geproduceerde gaat laatste lijst een dict zijn met tuples (opvals) als keys en tuples (xsec en error) als content
        try: 
            requestedVals = data[name][(op1,op2)]
        except:
            requestedVals = []
        for valPair in opVals:
            # The the boolean will be used to indicate whether the data is available, which TODO is his the way to go?
            requestedVals.append((valPair,False))
        data.update({name: {(op1,op2): requestedVals}})
        numpy.savez("requested.npz", index=index, data=data)

def listNames():
    try:
        index = numpy.load("requested.npz")["index"].item()
    except:
        index = {}
    finally:
        print('\n############### Available names: ###############')
        for name in index.keys():
            print(name + ': ' + repr(index[name]))
        print(' ')

# what function args.func() calls depends on the subparser being called 
def go():
    if(args.subparser_name =="add"):
        addRequests(name, op1, op2, opVals)
    # elif(args.subparser_name =="remove"):
    elif(args.subparser_name =="addName"):
        addName(name=args.name, model=args.model, procTemplate=args.procTemplate, restrictSet=args.restrictSet)
    # elif(args.subparser_name =="removeName"):
    elif(args.subparser_name =="listNames"):
        listNames()
    else:
        print("That it not an available action, get some --help")
        return
# this makes sure that order.py runs as it should when started, but doesn't run when imorporting it from another script (strange but standard python behaviour)
if __name__ == "__main__":
    go()



















# CODE DUMP BELOW, HERE BE DRAGONS
# def interface():
    # if(args.action in ['add','request','a','r']):
    #     if(args.specific):
    #         addScan
    #     else:

    # if(args.action in ['delete','d']):
    #     if(specific):
    #         delete(     )
    #     else:
    #         deleteAll()
    # if(args.action in ['addname','addName']):
        
    # if(args.action in ['removename','removeName']):

    # else:
    #     print("No action to be performed specified, check --help")
    #     return