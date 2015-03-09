#!/usr/bin/env python3

__author__ = 'nick.york'
__license__ = 'https://www.apache.org/licenses/LICENSE-2.0'
__copyright__ = 'Copyright (c) 2015 Virtual Instruments Corporation. All rights reserved.'
__date__ = '2015-03-09'
__version__ = '1.0'

# parses the output of the following Cisco commands to build aliases
# show fcalias
# show zone
# show zoneset
# show zoneset active
# show flogi database
# show fcns database
# show device-alias database

import optparse, os, sys
import re

def ParseCmdLineParameters():
    opts = optparse.OptionParser(description='Convert Cisco show output to CSV.')
    opts.add_option("-i", "--input", action="store", type="string", dest="input")
    opts.add_option("-o", "--output", action="store", type="string", dest="output")
    opt, argv = opts.parse_args()

    return opt

def PrintHelpAndExit(errormessage=""):
    if (errormessage != ""):
        print("\n\n" + errormessage)
    print("\n\nUsage:\n\tCiscoAliasesToCSV.py [-i <Input Text File>] [-o <Output CSV>]\n\n\tIf -i is not specified, input will be read from stdin.\n\tIf -o is not specified, CSV will be output to stdout.\n\n")
    exit()

def ParseAliases(fh):
    # device aliases are contained on a single line
    re_devalias = re.compile("^device-alias name (.*?) pwwn ([0-9a-f]{2}:?[0-9a-f]{2}:?[0-9a-f]{2}:?[0-9a-f]{2}:?[0-9a-f]{2}:?[0-9a-f]{2}:?[0-9a-f]{2}:?[0-9a-f]{2})$")
    # fcaliases are defined on two lines, the first defining the name and the second containing the pwwn
    # technically fcaliases can contain more than 1 wwn, but not handling that case
    re_fcalias1 = re.compile("^fcalias name (.*?) vsan \d+$")
    re_fcalias2 = re.compile("^.*?pwwn ([0-9a-f]{2}:?[0-9a-f]{2}:?[0-9a-f]{2}:?[0-9a-f]{2}:?[0-9a-f]{2}:?[0-9a-f]{2}:?[0-9a-f]{2}:?[0-9a-f]{2}).*$")

    alias = None
    wwn = None
    aliases = {}

    for line in fh.readlines():
        # if there's an alias left over it means we are likely in the 2nd line of a fcalias match
        if alias != None:
            m = re_fcalias2.match(line)
            if m:
                wwn = m.group(1)
            else:
                # since we are not in fact in a fcalias match, clear the alias
                alias = None
        else:
            # check for device alias match
            m = re_devalias.match(line)
            if m:
                alias = m.group(1)
                wwn = m.group(2)
            else:
                # otherwise check for the first line of an fcalias match
                m = re_fcalias1.match(line)
                if m:
                    alias = m.group(1)
        # if we have an alias and wwn then add it to the list
        if alias != None and wwn != None:
            # key on wwn so we don't get duplicate aliases
            aliases[wwn] = alias
            alias = None
            wwn = None

    return aliases

def main():
    options = ParseCmdLineParameters()

    if options.input != None:
        inputfile = open(options.input,'r')
    else:
        inputfile = sys.stdin

    aliases = ParseAliases(inputfile)

    if options.output != None:
        output = open(options.output, 'w')
    else:
        output = sys.stdout

    for alias in aliases:
        output.write("{0},{1}\n".format(alias, aliases[alias]))

if __name__ == '__main__':
    main()
