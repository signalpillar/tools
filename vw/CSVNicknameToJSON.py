#!/usr/bin/env python3

__author__ = 'nick.york'
__license__ = 'https://www.apache.org/licenses/LICENSE-2.0'
__copyright__ = 'Copyright (c) 2015 Virtual Instruments Corporation. All rights reserved.'
__date__ = '2015-02-22'
__version__ = '1.0'

import sys, os, optparse
import json

class Entity:
    def __init__(self, name, wwn):
        self.name = name
        self.wwn = wwn
        self.type = "fcport"
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
    print("\n\nUsage:\n\tCSVNicknameToJSON -i <Input CSV> -o <Output JSON>\n\n\tIf input or output are not specified, stdin and stdout are used, respectively.\n\n\t\tpython3 CSVNicknameToJSON.py -i input.csv -o output.json\n\n\t\tcat input.csv | python3 CSVNickNameToJSON.py | python3 EntityImport.py -v 10.20.30.40 -u Administrator -p admin\n\n\t\tInput file should be in the format WWN,Nickname with one entry per line.\n\n")
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

    # iterate through the input file .. WWN,Nickname
    for line in fi:
        if not "," in line:
            continue
        # create a new object and stuff it in the top container
        top.entities.append(Entity(line.split(',')[1].strip().replace("'","").replace('"',""), line.split(',')[0].strip()))

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