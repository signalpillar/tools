#!/usr/bin/env python3

__author__ = 'nick.york'
__license__ = 'https://www.apache.org/licenses/LICENSE-2.0'
__copyright__ = 'Copyright (c) 2015 Virtual Instruments Corporation. All rights reserved.'
__date__ = '2015-03-08'
__version__ = '1.0'

import optparse, os, sys
import re

devicetypewwns = [('20:?00:?00:?25:?b5.*', 'Host'), # Cisco UCS
                  ('2[0-9a-fA-F]:?[0-9a-fA-F][0-9a-fA-F]:?00:?2a:?6a.*', 'Host'), # Cisco UCS
                  ('2[0-9a-fA-F]:?[0-9a-fA-F][0-9a-fA-F]:?00:?11:?0a.*', 'Host'), # HP VC
                  ('50:?01:?4c:?2.*', 'Host'), # HP NIV
                  ('10:?00:?38:?9d:?30:?6.*', 'Host'), # HP
                  ('10:?00:?00:?11:?0a:?03.*', 'Host'), # HP
                  ('50:?01:?43:?80.*', 'Host'), # HP VCEM
                  ('c0:?50:?76.*', 'Host'), # IBM LPAR
                  ('22:?02:?00:?02.*', 'StorageArray'), # HP 3PAR
                  ('23:?02:?00:?02.*', 'StorageArray'), # HP 3PAR
                  ('50:?00:?14:?42.*', 'StorageArray'), # VPLEX
                  ('50:?05:?07:?68:?01.*', 'StorageArray'), # SVC
                  ('50:?06:?01:?6.*', 'StorageArray'), # EMC
                  ('50:?06:?04:?8.*', 'StorageArray'), # EMC
                  ('50:?00:?09:?7.*', 'StorageArray'), # EMC
                  ('50:?06:?0e:?80.*', 'StorageArray'), # HDS
                  ('50:?05:?07:?6.*', 'StorageArray'), # IBM
                  ('50:?0a:?09:?8.*', 'StorageArray'), # NetApp
                  ('52:?4a:?93:?7.*', 'StorageArray'), # Pure

                    ('10.*', 'Host'), # Default Host
                    ('20.*', 'Host'), # Default Host
                    ('50.*', 'StorageArray') # Default Storage
                ]

regexpatterns = ['^(.*)[_-]hba[_-]?\d+$', '^(.*)[_-]fcs[_-]?\d+$', '^(.*)[_-]\d$']

def ParseCmdLineParameters():
    opts = optparse.OptionParser(description='Create Entities from an Alias CSV File.')
    opts.add_option("-i", "--input", action="store", type="string", dest="input")
    opts.add_option("-o", "--output", action="store", type="string", dest="output")
    opts.add_option("-s", "--storagewwns", action="store", type="string", dest="storagewwns")
    opts.add_option("-w", "--hostwwns", action="store", type="string", dest="hostwwns")
    opts.add_option("-r", "--regex", action="store", type="string", dest="regex")
    opts.add_option("-z", "--strip", action="store", type="string", dest="strip")
    opt, argv = opts.parse_args()

    if opt.hostwwns != None:
        a = opt.hostwwns.split(',')
        a.reverse()
        for wwn in a:
            devicetypewwns.insert(0, (wwn, 'Host'))
    if opt.storagewwns != None:
        a = opt.storagewwns.split(',')
        a.reverse()
        for wwn in a:
            devicetypewwns.insert(0, (wwn, 'StorageArray'))
    if opt.regex != None:
        a = opt.regex.split(',')
        a.reverse()
        for r in a:
            regexpatterns.insert(0, r)

    return opt

def PrintHelpAndExit(errormessage=""):
    if (errormessage != ""):
        print("\n\n" + errormessage)
    print("\n\nUsage:\n\tAliasesToEntities.py [-i <aliases.csv>][,<aliases.csv>] [-o <output.csv>] [-s <storagewwnpattern>] [-w <hostwwnpattern>] [-r <regex pattern>] [-z <skip string>]\n\n")
    print("\tIf -i is not specified, aliases will be read from stdin.\n")
    print("\tIf -o is not specified, output will go to stdout.\n")
    print("\tstorageportwwnpatterns and hostwwnpatterns can be used to override the default host or storage assignment and should be specified one or more comma separated, in regex pattern (-s 50.*,60.*,70.*)\n")
    print("\tregex patterns should be specified comma separated (-r ""^(.*)_hba\d+$""\n")
    print("\t--strip allows you to remove strings anywhere in the alias, for example SANA_HOSTNAME_HBA you could specify -z SANA_,SANB_ to strip off the beginning part\n")
    print("\n\tExample: python3 AliasesToEntities.py -i alias_a.csv,alias_b.csv -o output.csv -z DC1_ -r ""^(.*?)_.*$""\n")

    exit()

def ReadAliases(fh):
    aliasesdict = {}
    for line in fh.readlines():
        aliasesdict[line.split(',')[1].strip()] = line.split(',')[0]

    return aliasesdict

def StripStrings(aliasesdict, strings):
    newaliasesdict = {}
    for alias in aliasesdict.keys():
        newalias = alias
        for str in strings:
            if str in newalias:
                newalias = newalias.replace(str,'')
        newaliasesdict[newalias] = aliasesdict[alias]

    return newaliasesdict

def FindEntities(aliasesdict):
    entities = {}
    for alias in aliasesdict.keys():
        for pattern in regexpatterns:
            r = re.match(pattern, alias)
            if r:
                rootname = r.group(1)
                if rootname in entities:
                    entities[rootname].append(aliasesdict[alias])
                else:
                    entities[rootname] = [aliasesdict[alias]]

                break  # found a match, continue to next alias

    return entities

def HostOrStorage(wwn):
    for entry in devicetypewwns:
        if re.match(entry[0], wwn):
            return entry[1]

    return "Host"

def main():
    options = ParseCmdLineParameters()

    aliasesdict = {}
    # get aliases from the provided text file, or standard input if no file provided
    if options.input != None:
        for inputfile in options.input.split(','):
            aliasesdict.update(ReadAliases(open(inputfile,'r')))
    else:
        aliasfile = sys.stdin
        aliasesdict.update(ReadAliases(aliasfile))

    # strip out any specified character strings
    if options.strip !=  None:
        aliasesdict = StripStrings(aliasesdict, options.strip.split(","))

    # parse regular expressions
    entities = FindEntities(aliasesdict)

    # output entities to output file or standard output
    if options.output != None:
        output = open(options.output, 'w')
    else:
        output = sys.stdout

    # assign host or storage type based on input and defaults
    for entity in entities.keys():
        output.write("{0},{1},{2}\n".format(HostOrStorage(entities[entity][0]), entity, ','.join(entities[entity])))

if __name__ == '__main__':
    main()