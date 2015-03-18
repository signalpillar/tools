#!/usr/bin/env python3

__author__ = 'nick.york'
__license__ = 'https://www.apache.org/licenses/LICENSE-2.0'
__copyright__ = 'Copyright (c) 2015 Virtual Instruments Corporation. All rights reserved.'
__date__ = '2015-02-22'
__version__ = '1.0'

# requires python requests module by Kenneth Reitz
# http://docs.python-requests.org/en/latest/
# git clone git://github.com/kennethreitz/requests.git
# pip3 install requests
import requests
import json
import sys, os, optparse

jsonheaders = {'content-type': 'application/json'}
requests.packages.urllib3.disable_warnings()
s = requests.session()

def ParseCmdLineParameters():
    opts = optparse.OptionParser(description='Upload a JSON Entity Import File to VirtualWisdom.')
    opts.add_option("-v", "--virtualwisdom", action="store", type="string", dest="host")
    opts.add_option("-u", "--username", action="store", type="string", dest="username")
    opts.add_option("-p", "--password", action="store", type="string", dest="password")
    opts.add_option("-z", "--password-file", action="store", type="string", dest="passwordfile")
    opts.add_option("-f", "--file", action="store", type="string", dest="filename")
    opts.add_option("-i", "--stdin", action="store_true", dest="stdin", default=False)
    opts.add_option("-F", "--force", action="store_true", dest="force", default=False)
    opt, argv = opts.parse_args()

    if opt.host == None or opt.username == None or (opt.password == None and opt.passwordfile == None) or (opt.filename == None and not opt.stdin):
        PrintHelpAndExit("You must specify the VirtualWisdom host, username, password or password file and file to import or stdin.")
        exit()

    if opt.passwordfile != None:
        if not os.path.exists(opt.passwordfile):
            PrintHelpAndExit("Specified password file does not exist.")

    if opt.filename != None:
        if not os.path.exists(opt.filename):
            PrintHelpAndExit("Specified entity file does not exist.")

    return opt


def PrintHelpAndExit(errormessage=""):
    if (errormessage != ""):
        print("\n\n" + errormessage)
    print("\n\nUsage:\n\tEntityImport -v <VW Appliance IP> -u <Username> -p <Password> -f <Entity Import File>\n\n\tEntityImport -v <VW Appliance IP> -u <Username> -z <PasswordFile> -f <Entity Import File>\n\n\t\techo 'admin' > pwfile\n\t\tchmod 600 pwfile\n\t\tpython3 EntityImport.py -v 10.20.30.40 -u Administrator -z pwfile -f import.json\n\n")
    exit()

# the server will do a much more thorough job of validating
# this is just making sure that the user has really specified a json file
# and that it has a version, before we start logging into VW
def ValidateJSON(fh=None,str=None):
    try:
        if fh is not None:
            inputobject = json.load(fh)
        else:
            inputobject = json.loads(str)
    except ValueError as e:
        PrintHelpAndExit("Provided JSON could not be parsed.\n\n" + e)
    if ("version" not in inputobject or inputobject["version"] != 1):
        PrintHelpAndExit("Provided JSON does not conform to VW4 Entity Import standard.  Version number mismatch.")
    if ("entities" not in inputobject or len(inputobject["entities"]) == 0):
        PrintHelpAndExit("Provided JSON contains no entities.")
    return True

# logs into VirtualWisdom using the provided credentials
# on the global session
def VirtualWisdomLogin(ipaddr, login, password):
    loginpayload = {'username': login, 'password': password, 'targetRoute': None}
    try:
        # undocumented and unsupported apis, subject to change in every release
        r = s.post('https://{0}/api/sec/login'.format(ipaddr), verify=False, data=loginpayload)
        if r.status_code == 200:
            # undocumented and unsupported apis, subject to change in every release
            r = s.get('https://{0}/api/sec/session'.format(ipaddr), verify=False)
            if r.json()['status'] == "OK":
                return
            else:
                PrintHelpAndExit("Logged into VirtualWisdom but session check was unsuccessful.")
        else:
            PrintHelpAndExit("Unable to connect to VirtualWisdom with provided information.")
    except:
        PrintHelpAndExit("Exception caught in the VirtualWisdom login process.")

# uploads entity import file, checks validation and commits changes if validation successful
def UploadEntityImport(ipaddr, fh=None, str=None, force=False):
    #try:
    # undocumented and unsupported apis, subject to change in every release
    if fh is not None:
        r = s.post('https://%s/api/config/entity/import/start' % (ipaddr), verify=False, data=fh, headers=jsonheaders)
    else:
        r = s.post('https://%s/api/config/entity/import/start' % (ipaddr), verify=False, data=str, headers=jsonheaders)
    if r.status_code == 200 and r.json()['status'] == "OK":
        transactionid = r.json()['result']['transactionId']
        commitpayload = {"transactionId":transactionid,"async":"true"}
        # undocumented and unsupported apis, subject to change in every release
        r = s.put('https://{0}/api/config/entity/import/commit'.format(ipaddr), verify=False, data=json.dumps(commitpayload), headers=jsonheaders)
        return True
    else:
        # loop through the errors and print them all out
        for entity in r.json()['result']['entities']:
            try:
                print("\nMessage: " + entity['marker']['message'])
                print("Entity: {0} [{1}]".format(entity['name'], entity['type']))
                print("Location: Line: {0} Column: {1}".format(entity['marker']['location']['line'], entity['marker']['location']['column']))
            except:
                pass

        if not force:
            print("\n\nValidation failure.  To attempt to import anyway run again with --force\n")
            exit()
        else:
            transactionid = r.json()['result']['transactionId']
            commitpayload = {"transactionId":transactionid,"async":"true"}
            # undocumented and unsupported apis, subject to change in every release
            r = s.put('https://{0}/api/config/entity/import/commit'.format(ipaddr), verify=False, data=json.dumps(commitpayload), headers=jsonheaders)
            if r.status_code == 200 and r.json()['status'] == "OK":
                return True
            else:
                print(r.status_code)
                print(r.json()['status'])
                print("Force failed.")
                exit()
    #except:
    #    PrintHelpAndExit("Exception caught during Entity Import.")


def main():
    options = ParseCmdLineParameters()

    # if the user specified an entity file, use it otherwise read from standard input
    if options.filename != None:
        ValidateJSON(fh=open(options.filename, 'r'))
    else:
        stdinstring = ''.join(sys.stdin.readlines())
        ValidateJSON(str=stdinstring)

    # if the user specified a password use it, otherwise read from the provided password file
    if options.password != None:
        VirtualWisdomLogin(options.host, options.username, options.password)
    else:
        VirtualWisdomLogin(options.host, options.username, open(options.passwordfile,'r').readline().strip())

    # if the user specified an entity file, use it otherwise read from standard input
    if options.filename != None:
        UploadEntityImport(options.host, fh=open(options.filename, 'r'), force=options.force)
    else:
        UploadEntityImport(options.host, str=stdinstring, force=options.force)
    print("Successfully Imported!")

if __name__ == '__main__':
    main()