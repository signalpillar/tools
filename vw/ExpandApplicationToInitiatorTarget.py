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
    opts.add_option("-a", "--application", action="store", type="string", dest="application")
    opts.add_option("-e", "--hostlist", action="store", type="string", dest="hostlist")
    opts.add_option("-n", "--newname", action="store", type="string", dest="newname")
    opts.add_option("-o", "--output", action="store", type="string", dest="output")
    opt, argv = opts.parse_args()

    if opt.host == None or opt.username == None or (opt.password == None and opt.passwordfile == None) or (opt.application == None and opt.hostlist == None) or opt.newname == None:
        PrintHelpAndExit("You must specify the VirtualWisdom host, username, password or password file and application or host list and a new name for the application.")
        exit()

    if opt.passwordfile != None:
        if not os.path.exists(opt.passwordfile):
            PrintHelpAndExit("Specified password file does not exist.")

    return opt


def PrintHelpAndExit(errormessage=""):
    if (errormessage != ""):
        print("\n\n" + errormessage)
    print("\n\nUsage:\n\tExpandApplicationToInitiatorTarget.py -v <VW Appliance IP> -u <Username> [-p <Password>|-z <pwfile>] -a <Application Name> -n <New Application Name>\n\n\tExpandApplicationToInitiatorTarget.py -v <VW Appliance IP> -u <Username> [-p <Password>|-z <pwfile>] -e <Host>[,<Host][,<Host>] -n <New Application Name>\n\n")
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

def GetEntityId(ipaddr, entity, entitytype):
    # undocumented and unsupported apis, subject to change in every release
    r = s.get('https://{0}/api/entitymgmt/entities?filter={1}&filterKeys=DisplayLabel%2CTags&filterValues={1}&type={2}&page=1&start=0&limit=500000'.format(ipaddr, entity, entitytype), verify=False)
    if r.status_code == 200 and r.json()['status'] == "OK":
        for e in r.json()['result']['data']:
            if e['DisplayLabel'] == entity:
                return e['Id']

def GetTopology(ipaddr, entityid, fab1):
    payload = {"appId":"-1","hostFilter":{"type":"HostPort","entityIds":[entityid]},"storageFilter":{"type":"StoragePort"}}

    # undocumented and unsupported apis, subject to change in every release
    r = s.put('https://{0}/api/topo/filter4/graph'.format(ipaddr), data=json.dumps(payload), headers=jsonheaders, verify=False)
    storageports = []
    if r.status_code == 200 and r.json()['status'] == "OK":
        for node in r.json()['result']['nodes']:
            if 'DeviceType' in r.json()['result']['nodes'][node] and r.json()['result']['nodes'][node]['DeviceType'] == 'STORAGE':
                fab2 = GetFabric(ipaddr, r.json()['result']['nodes'][node]['Id'])
                if fab1 == fab2:
                    storageports.append(r.json()['result']['nodes'][node]['DisplayLabel'])

    return storageports

def GetHBAs(ipaddr, entityid, entitytype):
    if entitytype == 'Application':
        payload = {"appId":entityid,"hostFilter":{"type":"HostPort"}}
    else:
        payload = {"appId":"-1","hostFilter":{"type":"HostPort","entityIds":[entityid]}}

    # undocumented and unsupported apis, subject to change in every release
    r = s.put('https://{0}/api/topo/filter4/graph'.format(ipaddr), data=json.dumps(payload), headers=jsonheaders, verify=False)
    hbas = []
    if r.status_code == 200 and r.json()['status'] == "OK":
        for node in r.json()['result']['nodes']:
            if 'DeviceType' in r.json()['result']['nodes'][node] and r.json()['result']['nodes'][node]['DeviceType'] == 'SERVER':
                hbas.append((r.json()['result']['nodes'][node]['DisplayLabel'], r.json()['result']['nodes'][node]['Id']))

    return hbas

def GetFabric(ipaddr, entityid):
    # undocumented and unsupported apis, subject to change in every release
    r = s.get('https://{0}/api/entitymgmt/entity/properties?ids={1}&withArchived=false'.format(ipaddr, entityid), verify=False)
    if r.status_code == 200 and r.json()['status'] == "OK":
        return r.json()['result'][0]['LogicalFabric DisplayLabel']

def main():
    options = ParseCmdLineParameters()

    # if the user specified a password use it, otherwise read from the provided password file
    if options.password != None:
        VirtualWisdomLogin(options.host, options.username, options.password)
    else:
        VirtualWisdomLogin(options.host, options.username, open(options.passwordfile,'r').readline().strip())

    topo = {}
    if options.application != None:
        entityid = GetEntityId(options.host, options.application, 'Application')
        hbas = GetHBAs(options.host, entityid, 'Application')
        for hba in hbas:
            fab = GetFabric(options.host, hba[1])
            topo[hba] = GetTopology(options.host, hba[1], fab)
    else:
        for entity in options.hostlist.split(","):
            entityid = GetEntityId(options.host, entity.strip(), 'Host')
            hbas = GetHBAs(options.host, entityid, 'Host')
            for hba in hbas:
                fab = GetFabric(options.host, hba[1])
                topo[hba] = GetTopology(options.host, hba[1], fab)
    line = "Application,{0}".format(options.newname)
    for hba in topo:
        for targ in topo[hba]:
            line += ",{0}:{1}".format(hba[0], targ)
    print(line)

    print("\n")

if __name__ == '__main__':
    main()