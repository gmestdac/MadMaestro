import argparse
import os
import io
import numpy
import pprint 
import itertools
import glob

argParser = argparse.ArgumentParser(description = "Argument parser for MadMaesto. get help for any of the functions below by typing its name before --help")
subparsers = argParser.add_subparsers(dest='subparser_name')

add_Parser = subparsers.add_parser('add')
remove_Parser = subparsers.add_parser('remove')
addName_Parser = subparsers.add_parser('addName')
removeName_Parser = subparsers.add_parser('removeName')
listNames_Parser = subparsers.add_parser('listNames')
listData_Parser = subparsers.add_parser('listData')

try:
    index = numpy.load("requested.npz")["index"].item()
    avNames = index.keys()
except:
    avNames = {}

# argument parser for adding datapoints
add_Parser.add_argument('name',                     action='store',    choices=avNames,                     help="Name op the dataset to add requests to")
add_Parser.add_argument('-c','--coeff',             action='append',        nargs=4,                        help="Scan over a coefficient, needs 4 arguments: coefficient, begin, end, number of values. Add this multiple times to perform 2D scans pairs of all speciefied operators. The SM case will always be included.", metavar=('COEFF', 'BEGIN', 'END', 'NUMBER'))
add_Parser.add_argument('-n','--nEvents',           action='store',         default = 10000,    type=int,   help="Number of Events" )
add_Parser.add_argument('-o','--overwrite',         action='store_true',    default=False,                  help="Overwrite exisiting results, deletion of existing files and results is done when requesting")
add_Parser.add_argument('--keepWorkspace',          action='store_true',    default=False,                  help="keep the MadGraph event folder?")
add_Parser.add_argument('-s',"--specific",          action="append",        nargs=4,                        help="Define specific coefficient values instead of scanning. Can be specified multiple times. Format: c1 c2 c1value c2value. If c1=c2 adds c1value 1 and 2 to the corresponding 1D data")

# argument parser for removing datapoints
remove_Parser.add_argument('name',                  action='store', choices=avNames,                        help="Name op the dataset to add requests to")
remove_Parser.add_argument('-c','--coeff',          action='append',                                        help= "remove data associated with this coefficient, specifying mutiple operators (-c in front of each) removes data associated with each possible coefficient pair")
remove_Parser.add_argument('-s',"--specific",       action="append",        nargs=4,                        help="Remove only data corresponding to specific coefficient values. Can be specified multiple times. Format: c1 c2 c1value c2value")

# argument parser for adding a dataset name
addName_Parser.add_argument('name',                 action='store',                                         help="Name to associate with this dataset")
addName_Parser.add_argument('model',         action='store',         choices=['HEL', 'dim6top_LO', 'dim6top_LO_v2'], help="Which madgraph model to use?")
addName_Parser.add_argument('procTemplate',         action='store',                                         help="Specify the process card template")
addName_Parser.add_argument('restrictSet',          action='store',   default='A',                          help="Specify template label (A,B,C,...),  ")
removeName_Parser.add_argument('name',              action='store',         nargs='+',  choices=avNames,                      help="Provide any number of names to be removed")

# argument parser for listing Names and associated info 
listNames_Parser.add_argument('--name','-n',        action='store',         default="listall", choices=avNames, help="Get info on a specific name instead if listing them all")

listData_Parser.add_argument('--name','-n',         action='store',         default="listall", choices=avNames, help="Get info on a specific name instead if listing them all")
listData_Parser.add_argument('-c','--coeff',        action='append',         default="listall", help="Get info on a specific coefficient (pair)")

args = argParser.parse_args()

# TODO list available options 
# TODO maak volgorde consistent door te sorten  AAN BEGIN VAN PROGRAMMA
# TODO converteer naar floats bij opslaan voor gemak later

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

    if not ( glob.glob("./MG5_aMC_v2_6_3_2/models/" + model + "_UFO/restrict_" + restrictSet + "*" ) ):  
        print("restrict card set is missing")
        return    
    index.update({name: [model, procTemplate, restrictSet]})
    numpy.savez("requested.npz", index=index, data=data)

def addRequests(name, op1, op2, opVals, overWrite, keepWorkspace, nEvents ):
    try:
        index = numpy.load("requested.npz")["index"].item()
    except:
        index = {}
    try:
        data = numpy.load("requested.npz")["data"].item()
    except:
        data = {}
    finally:
        # NOTE in geproduceerde gaat laatste lijst een dict zijn met tuples (opvals) als keys en tuples (xsec en error) als content
        try: 
            requestedVals = data[name][(op1,op2)]
        except:
            requestedVals = []
        for valPair in opVals:
            # The the boolean will be used to indicate whether the data is available, which TODO is his the way to go?
            requestedVals.append( tuple((valPair,False,overWrite, keepWorkspace, nEvents)) )
        # remove duplicates
        requestedVals.append( tuple(((0,0) , False, overWrite, keepWorkspace, nEvents)) )
        requestedVals = list(set(requestedVals))
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

def listData():
    pp = pprint.PrettyPrinter(indent=4)
    try:
        data = numpy.load("requested.npz")["data"].item()
    except:
        data = {}
    finally:
        print('\n############### Available Data: ###############')
        print('#green=available, red=to be overwritten, blue=requested#\n')
        for name in data.keys():
            for oppair in data[name].keys():
                print(repr(oppair))
                pairdata= data[name][oppair] 
                for entry in pairdata:
                    if(entry[1] and entry[2]):
                        print('yee')
                        print('\x1b[0;37;41m' + repr(entry[0]) + '\x1b[0m')
                    if(entry[1] and  not entry[2]):
                        print('yeh')
                        print('\x1b[0;37;42m' + repr(entry[0]) + '\x1b[0m')
                    if(not entry[1]):
                        print('yah')
                        print('\x1b[0;37;44m' + repr(entry[0]) + '\x1b[0m')
        print(' ')

# what function args.func() calls depends on the subparser being called 
def go():
    if(args.subparser_name =="add"):
        overWrite = args.overwrite
        if(len(args.coeff) == 0 ):
            print("no coefficient specified")
            return
        if(len(args.coeff) == 1 ):
            opVals = numpy.linspace(round(float(args.coeff[0][1]),4), round(float(args.coeff[0][2]),4), num=int(args.coeff[0][3]))
            addRequests(args.name, args.coeff[0][0], args.coeff[0][0], zip(opVals,opVals), overWrite, args.keepWorkspace, args.nEvents )
        else:
            coeffValList = []
            for i in range(0,len(args.coeff)-1):
                coeffValList.append( tuple( (args.coeff[i][0], numpy.linspace(float(args.coeff[i][1]), float(args.coeff[i][2]), num=int(args.coeff[i][3])).round(4) ) ) )
            combos = itertools.combinations(coeffValList, 2)
            combos = sorted(combos, key=lambda x: x[0])
            for pair in combos:
                addRequests(args.name, pair[0][0], pair[1][0], zip(pair[0][1],pair[0][1]), overWrite, args.keepWorkspace, args.nEvents )

    # elif(args.subparser_name =="remove"):
    elif(args.subparser_name =="addName"):
        addName(name=args.name, model=args.model, procTemplate=args.procTemplate, restrictSet=args.restrictSet)
    # elif(args.subparser_name =="removeName"):
    elif(args.subparser_name =="listNames"):
        listNames()
    elif(args.subparser_name =="listData"):
        listData()
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