#!/usr/bin/env python3

__author__ = 'nick.york'
__license__ = 'https://www.apache.org/licenses/LICENSE-2.0'
__copyright__ = 'Copyright (c) 2015 Virtual Instruments Corporation. All rights reserved.'
__date__ = '2015-02-24'
__version__ = '1.0'

import optparse, os, sys

def ParseCmdLineParameters():
    opts = optparse.OptionParser(description='Convert Brocade AliShow output to CSV.')
    opts.add_option("-a", "--alishow", action="store", type="string", dest="alishow")
    opts.add_option("-s", "--switchshow", action="store", type="string", dest="switchshow")
    opts.add_option("-o", "--output", action="store", type="string", dest="output")
    opt, argv = opts.parse_args()

    return opt


def PrintHelpAndExit(errormessage=""):
    if (errormessage != ""):
        print("\n\n" + errormessage)
    print("\n\nUsage:\n\tBrocadeAliShowToCSV.py [-a <AliShow Text File>] [-s <SwitchShow Text File>] [-o <Output CSV>]\n\n\tIf -a is not specified, AliShow will be read from stdin.\n\tIf -s is not specified, SwitchShow will not be used.\n\tIf -o is not specified, CSV will be output to stdout.\n\n")
    exit()

def ParseSwitchShow(fh):
    print("Parsing SwitchShow...")
    portloginsbyslotport = {}
    portloginsbyindex = {}
    for line in fh.readlines():
        if(not line.split()[0].isdigit()) or ":" not in line:
            continue
        else:
            if len(line.split()) >= 10:
                portloginsbyslotport[(line.split()[1], line.split()[2])] = line.split()[9]
                portloginsbyindex[line.split()[0]] = line.split()[9]

    return portloginsbyindex

def ParseAliShow(fh, portlogins):
    print("Parsing AliShow...")
    aliases = {}
    for line in fh.readlines():
        if "alias:" in line:
            alias = line.split(":")[1].strip()
        elif "," in line:
            if line.split(",")[1].strip() in portlogins:
                aliases[alias] = portlogins[line.split(",")[1].strip()]
        elif ":" in line:
            aliases[alias] = line.strip()

    return aliases

def main():
    options = ParseCmdLineParameters()

    if options.alishow != None:
        print("Opening AliShow")
        alishow = open(options.alishow,'r')
    else:
        alishow = sys.stdin

    portlogins = {}

    if options.switchshow != None:
        print("Opening SwitchShow")
        switchshow = open(options.switchshow, 'r')
        portlogins = ParseSwitchShow(switchshow)

    aliases = ParseAliShow(alishow, portlogins)

    if options.output != None:
        output = open(options.output, 'w')
    else:
        output = sys.stdout

    print("Writing Output")
    for alias in aliases:
        output.write("{0},{1}\n".format(aliases[alias], alias))

if __name__ == '__main__':
    main()