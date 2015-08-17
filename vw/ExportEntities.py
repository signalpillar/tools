"""
Usage:
    vw_export_entities -v <VW Appliance IP> -u <Username> -p <Password> -e <Entity Name>

    vw_export_entities -v <VW Appliance IP> -u <Username> -z <PasswordFile> -t <Entity Type>

    echo 'admin' > pwfile
    chmod 600 pwfile
    vw_export_entities -v 10.20.30.40 -u Administrator -z pwfile -t Application

"""

__author__ = 'nick.york'
__license__ = 'https://www.apache.org/licenses/LICENSE-2.0'
__copyright__ = 'Copyright (c) 2015 Virtual Instruments Corporation. All rights reserved.'
__date__ = '2015-02-22'
__version__ = '1.0'

# std
import argparse
import sys

# local
from vw.api.core import create_api_client_cli_parser, create_api_client
from vw.api.entity import EntityApi, EntityType


def ParseCmdLineParameters():

    parser = argparse.ArgumentParser(
        description='Upload a JSON Entity Import File to VirtualWisdom.',
        parents=[create_api_client_cli_parser()],
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-o", "--output", action="store", dest="output")
    parser.add_argument("-e", "--entity", action="store", dest="entity", help="Entity pattern")
    parser.add_argument("-t", "--entitytype", action="store", dest="entitytype")
    parser.add_argument("-s", "--properties", action="store_true", dest="properties", default=False)
    parser.add_argument("-x", "--exactonly", action="store_true", dest="exactonly", default=False)

    opt = parser.parse_args(sys.argv[1:])

    return opt


ENTITY_PROJECTION_BY_TYPE = dict(
    DEFAULT='DisplayLabel Type Tags Description BeginTime Id'.split(),
    HostPort='DisplayLabel Type Tags Description WWN BeginTime Id'.split(),
    StoragePort='DisplayLabel Type Tags Description BeginTime Id'.split(),
    Application='DisplayLabel Type Tags Description BeginTime Id Itls'.split(),
)


def get_projection_by_type(entity_type):
    return ENTITY_PROJECTION_BY_TYPE.get(entity_type, ENTITY_PROJECTION_BY_TYPE.get('DEFAULT'))


def export_by_entity_pattern(api, entity):
    entitylist = []
    for entitytype in EntityType:
        entitytype = entitytype.value

        items = api.find_entities_by_pattern(entity, entitytype)

        for e in items:
            if e['Type'] == 'Application':
                itls = []
                itls_items = api.find_itls_by_id(e['Id'], filter_keys=('initiatorLabel', 'targetLabel'))

                for i in itls_items:
                    init = i['initiatorLabel'] if i['initiatorLabel'] != '' else 'All'
                    targ = i['targetLabel'] if i['targetLabel'] != '' else 'All'
                    lun = i['lun'] if i['lun'] != -1 else 'All'
                    itls.append((init, targ, lun))

                e['Itls'] = itls

        entitylist.extend(items)

    return entitylist


def export_by_entity_type(api, entitytype):
    return api.find_entities(
        filter_keys=('DisplayLabel', 'Tags'),
        entity_type=entitytype
    )


def main():
    options = ParseCmdLineParameters()

    api = EntityApi(create_api_client(options))
    entities = (
        export_by_entity_pattern(api, options.entity)
        if options.entity
        else export_by_entity_type(api, options.entitytype)
    )

    if options.entity:
        if options.exactonly:
            entities = (
                entity
                for entity in entities
                if entity['DisplayLabel'] == options.entity
            )
            print("\nExact Matches:")
        else:
            print("\nAll Matches:")
    else:
        print("\n{0} Entities:".format(options.entitytype))

    for e in entities:
        print(tuple(map(e.get, get_projection_by_type(e['Type']))))
        if options.properties:
            print(api.get_entity_properties(e['Id']))

if __name__ == '__main__':
    main()
