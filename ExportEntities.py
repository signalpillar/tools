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
    opts.add_option("-o", "--output", action="store", type="string", dest="output")
    opts.add_option("-e", "--entity", action="store", type="string", dest="entity")
    opts.add_option("-t", "--entitytype", action="store", type="string", dest="entitytype")
    opts.add_option("-s", "--properties", action="store_true", dest="properties", default=False)
    opts.add_option("-x", "--exactonly", action="store_true", dest="exactonly", default=False)
    opt, argv = opts.parse_args()

    if opt.host == None or opt.username == None or (opt.password == None and opt.passwordfile == None) or (opt.entity == None and opt.entitytype == None):
        PrintHelpAndExit("You must specify the VirtualWisdom host, username, password or password file and entity or entity type.")
        exit()

    if opt.passwordfile != None:
        if not os.path.exists(opt.passwordfile):
            PrintHelpAndExit("Specified password file does not exist.")

    return opt


def PrintHelpAndExit(errormessage=""):
    if (errormessage != ""):
        print("\n\n" + errormessage)
    print("\n\nUsage:\n\tEntityExport -v <VW Appliance IP> -u <Username> -p <Password> -e <Entity Name>\n\n\tEntityImport -v <VW Appliance IP> -u <Username> -z <PasswordFile> -t <Entity Type>>\n\n\t\techo 'admin' > pwfile\n\t\tchmod 600 pwfile\n\t\tpython3 EntityExport.py -v 10.20.30.40 -u Administrator -z pwfile -t Application\n\n")
    exit()

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

def EntityExport(ipaddr, entity):
    #try:
    # undocumented and unsupported apis, subject to change in every release
    entitylist = []
    for entitytype in ('Application', 'Host', 'HBA', 'HostPort', 'ESXCluster', 'ESXHost', 'VirtualMachine', 'StorageArray', 'StorageController', 'IOModule', 'StoragePort'):
        r = s.get('https://{0}/api/entitymgmt/entities?filter={1}&filterKeys=DisplayLabel%2CTags&filterValues={1}&type={2}&page=1&start=0&limit=500000'.format(ipaddr, entity, entitytype), verify=False)
        if r.status_code == 200 and r.json()['status'] == "OK":
            for e in r.json()['result']['data']:
                entitylist.append((e['DisplayLabel'], e['Type'], e['Tags'], e['Description'], e['BeginTime'], e['Id']))

    return entitylist
    #except:
    #    PrintHelpAndExit("Exception caught during Entity Import.")

def EntityTypeExport(ipaddr, entitytype):
    #try:
    # undocumented and unsupported apis, subject to change in every release
    r = s.get('https://{0}/api/entitymgmt/entities?filter=&filterKeys=DisplayLabel%2CTags&filterValues=&type={1}&page=1&start=0&limit=500000'.format(ipaddr, entitytype), verify=False)
    if r.status_code == 200 and r.json()['status'] == "OK":
        entitylist = []
        for entity in r.json()['result']['data']:
            entitylist.append((entity['DisplayLabel'], entity['Type'], entity['Tags'], entity['Description'], entity['BeginTime'], entity['Id']))
        return entitylist
    else:
        return []
    #except:
    #    PrintHelpAndExit("Exception caught during Entity Import.")

def GetProperties(ipaddr, entityid):
    r = s.get('https://{0}/api/entitymgmt/entity/properties?ids={1}&withArchived=false'.format(ipaddr, entityid), verify=False)
    if r.status_code == 200 and r.json()['status'] == "OK":
        return r.json()['result']

# itls associated with an application
# https://172.16.218.131/api/entitymgmt/app/87178f0b62a94056b14a8971850b8fb4/itls?
#     _dc=1424529745961&filterKeys=initiatorLabel&filterKeys=targetLabel&page=1&start=0&limit=10000
#
# {"status":"OK","result":{"totalCount":4,"data":[{"id":"7dbe03875ad84bd8a7c4aa6dfb4616b8","editType":null,"initiatorId":"b4997cd3e39c475f86b1285af37a61e4","initiatorLabel":"SVCS_UCS12","initiatorWWN":"","initiatorFCID":"","targetId":"-1","targetLabel":"","targetWWN":"","targetFCID":"","lun":-1},{"id":"772975e25e1e40399ec5e6154ab3d459","editType":null,"initiatorId":"28d376ddbf834f9d901f2dfe94c001af","initiatorLabel":"SVCS_UCS14","initiatorWWN":"","initiatorFCID":"","targetId":"-1","targetLabel":"","targetWWN":"","targetFCID":"","lun":-1},{"id":"5747154ed76e4746b544117599d45d18","editType":null,"initiatorId":"78c538cd2bd043109e79e6301ab7a13f","initiatorLabel":"SVCS_UCS13","initiatorWWN":"","initiatorFCID":"","targetId":"-1","targetLabel":"","targetWWN":"","targetFCID":"","lun":-1},{"id":"6af506b8c73f45e2b3c9f74946c7f238","editType":null,"initiatorId":"990e2a55169141249a055100fc4c2b91","initiatorLabel":"SVCS_UCS11","initiatorWWN":"","initiatorFCID":"","targetId":"-1","targetLabel":"","targetWWN":"","targetFCID":"","lun":-1}]}}

def main():
    options = ParseCmdLineParameters()

    # if the user specified a password use it, otherwise read from the provided password file
    if options.password != None:
        VirtualWisdomLogin(options.host, options.username, options.password)
    else:
        VirtualWisdomLogin(options.host, options.username, open(options.passwordfile,'r').readline().strip())

    # if the user specified an entity file, use it otherwise read from standard input
    if options.entity != None:
        entities = EntityExport(options.host, options.entity)
    else:
        entities = EntityTypeExport(options.host, options.entitytype)

    if options.entity != None:
        if options.exactonly:
            print("\nExact Matches:")
            for e in entities:
                if e[0] == options.entity:
                    print(e)
                    if options.properties:
                        print(GetProperties(options.host, e[5]))
        else:
            print("\nAll Matches:")
            for e in entities:
                print(e)
                if options.properties:
                    print(GetProperties(options.host, e[5]))
    else:
        print("\n{0} Entities:".format(options.entitytype))
        for e in entities:
            print(e)
            if options.properties:
                print(GetProperties(options.host, e[5]))

    print("\n")

if __name__ == '__main__':
    main()