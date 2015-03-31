#!/usr/bin/env python3

__author__ = 'nick.york'
__license__ = 'https://www.apache.org/licenses/LICENSE-2.0'
__copyright__ = 'Copyright (c) 2015 Virtual Instruments Corporation. All rights reserved.'
__date__ = '2015-02-22'
__version__ = '1.0'

import sys, os, optparse
import json

class Entity:
    def __init__(self, name, type, child_entities):
        self.name = name
        self.type = type
        self.child_entities = {"add": child_entities}
    def __lt__(self, other):
        return self.name < other.name
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=2)

class ApplicationEntity:
    def __init__(self, name, type, initiator_list):
        self.name = name
        self.type = type
        self.itl_patterns = []
        for i in initiator_list:
            if i.count(":") == 2:
                # I:T:L
                self.itl_patterns.append({"edit_type": "add", "initiator": i.split(":")[0], "target": i.split(":")[1], "lun": i.split(":")[2]})
            elif i.count(":") == 1:
                # I:T
                self.itl_patterns.append({"edit_type": "add", "initiator": i.split(":")[0], "target": i.split(":")[1] })
            else:
                self.itl_patterns.append({"edit_type": "add", "initiator": i})
    def __lt__(self, other):
        return self.name < other.name
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=2)

# container for all the applications so that we can json
class Top:
    def __init__(self):
        self.version = 1
        self.entities = []
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=2)

def ParseCmdLineParameters():
    opts = optparse.OptionParser(description='Convert CSV to JSON Entity Import File for VirtualWisdom.')
    opts.add_option("-i", "--input", action="store", type="string", dest="inputfile")
    opts.add_option("-o", "--output", action="store", type="string", dest="outputfile")
    opt, argv = opts.parse_args()

    if opt.inputfile != None:
        if not os.path.exists(opt.inputfile):
            PrintHelpAndExit("Specified input file does not exist.")

    return opt

def PrintHelpAndExit(errormessage=""):
    if (errormessage != ""):
        print("\n\n" + errormessage)
    print("\n\nUsage:\n\tCSVRelationsToJSON -i <Input CSV> -o <Output JSON>\n\n\tIf input or output are not specified, stdin and stdout are used, respectively.\n\n\t\tpython3 CSVRelationsToJSON.py -i input.csv -o output.json\n\n\t\tcat input.csv | python3 CSVRelationsToJSON.py | python3 EntityImport.py -v 10.20.30.40 -u Administrator -p admin\n\n\t\tInput file should be in the format EntityType,EntityName,Member[,Member][...][,Member] with one entry per line.\n\n\t\tFor Host, HBA, StorageArray, StorageController, IOModule member is just the alias of the item to add.\n\t\tFor Application, it should be specified as Initiator, Initiator:Target or Initiator:Target:LUN depending on how you wish to define the Application.\n\n")
    exit()

def main():
    options = ParseCmdLineParameters()

    # input should either come from a text file, or from stdin
    if options.inputfile != None:
        fi = open(options.inputfile, 'r')
    else:
        fi = sys.stdin

    # set up object to store the entries in so we can dump it to JSON when done
    top = Top()

    # iterate through the input file .. EntityType,Entity,Member[,Member][,Member][,Member]
    for line in fi:
        if line.count(",") < 2:
            continue
        type = line.split(",")[0].strip().replace("'","").replace('"',"")
        name = line.split(",")[1].strip().replace("'","").replace('"',"")
        members = []
        for member in line.replace("'","").replace('"',"").split(",")[2:]:
            members.append(member.strip())
        # create a new object and stuff it in the top container
        if type.lower() == 'application':
            top.entities.append(ApplicationEntity(name, type, members))
        else:
            top.entities.append(Entity(name, type, members))

    # output will go to a text file or to stdout if no file is specified
    if options.outputfile != None:
        fo = open(options.outputfile, 'w')
    else:
        fo = sys.stdout

    # export the python object to JSON
    with fo as outfile:
        outfile.write(top.to_JSON())

if __name__ == '__main__':
    main()