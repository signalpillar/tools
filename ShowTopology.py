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
    opt, argv = opts.parse_args()

    if opt.host == None or opt.username == None or (opt.password == None and opt.passwordfile == None) or opt.entity == None:
        PrintHelpAndExit("You must specify the VirtualWisdom host, username, password or password file and entity.")
        exit()

    if opt.passwordfile != None:
        if not os.path.exists(opt.passwordfile):
            PrintHelpAndExit("Specified password file does not exist.")

    return opt


def PrintHelpAndExit(errormessage=""):
    if (errormessage != ""):
        print("\n\n" + errormessage)
    print("\n\nUsage:\n\tShowTopology.py -v <VW Appliance IP> -u <Username> -p <Password> -e <Entity Name>\n\n")
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

def GetEntityId(ipaddr, entity):
    entitylist = []
    for entitytype in ('Application', 'Host', 'HBA', 'HostPort', 'ESXCluster', 'ESXHost', 'VirtualMachine', 'StorageArray', 'StorageController', 'IOModule', 'StoragePort'):
        # undocumented and unsupported apis, subject to change in every release
        r = s.get('https://{0}/api/entitymgmt/entities?filter={1}&filterKeys=DisplayLabel%2CTags&filterValues={1}&type={2}&page=1&start=0&limit=500000'.format(ipaddr, entity, entitytype), verify=False)
        if r.status_code == 200 and r.json()['status'] == "OK":
            for e in r.json()['result']['data']:
                if e['DisplayLabel'] == entity:
                    entitylist.append(e['Id'])

    return entitylist

def GetTopology(ipaddr, entityid):
    payload = {"appId":"-1","hostFilter":{"type":"HostPort","entityIds":[entityid]},"storageFilter":{"type":"StoragePort"},"hostEdgeFilter":{"type":"LogicalSwitch"},"storageEdgeFilter":{"type":"LogicalSwitch"}}
    # undocumented and unsupported apis, subject to change in every release
    r = s.put('https://{0}/api/topo/filter4/graph'.format(ipaddr), data=json.dumps(payload), headers=jsonheaders, verify=False)
    hbas = []
    switches = []
    storageports = []
    if r.status_code == 200 and r.json()['status'] == "OK":
        for node in r.json()['result']['nodes']:
            if 'DeviceType' in r.json()['result']['nodes'][node] and r.json()['result']['nodes'][node]['DeviceType'] == 'SERVER':
                hbas.append(r.json()['result']['nodes'][node]['DisplayLabel'])
            elif 'DeviceType' in r.json()['result']['nodes'][node] and r.json()['result']['nodes'][node]['DeviceType'] == 'STORAGE':
                storageports.append(r.json()['result']['nodes'][node]['DisplayLabel'])
            else:
                switches.append(r.json()['result']['nodes'][node]['DisplayLabel'])

    return (hbas, switches, storageports)

def main():
    options = ParseCmdLineParameters()

    # if the user specified a password use it, otherwise read from the provided password file
    if options.password != None:
        VirtualWisdomLogin(options.host, options.username, options.password)
    else:
        VirtualWisdomLogin(options.host, options.username, open(options.passwordfile,'r').readline().strip())

    entities = GetEntityId(options.host, options.entity)
    for entityid in entities:
        topo = GetTopology(options.host, entityid)
        print("Host Ports: {0}".format(', '.join(topo[0])))
        print("Switches: {0}".format(', '.join(topo[1])))
        print("Storage Ports: {0}".format(', '.join(topo[2])))

    print("\n")

if __name__ == '__main__':
    main()