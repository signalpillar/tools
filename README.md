# Tools
Unsupported tools for interfacing with VirtualWisdom. Tools are a set of scripts to import and export data from the VW Appliance.


# Installation

Run the following command to get scripts installed:

    pip install -e git+https://github.com/Virtual-Instruments/tools.git\#egg=vw-tools-py

# Run tests

    tox 

# Supported use cases.

### Validate and import an entity import file to a VW.

Usage:

    vw_import_entities -v <VW Appliance IP> -u <Username> {-p <Password>|-z <Password File>} {-f <Entity Import File>|-i}

### Convert CSV WWN, nickname to an entity import file.

Usage:

    vw_csv_nickname_to_json [-i <Input File>] [-o <Output File>]

### Convert CSV EntityType, EntityName, Members to an entity import file.

Usage:

    vw_csv_relations_to_json [-i <Input File>] [-o <Output File>]

### Export entity details to CSV, by entity type or search by name.

Usage:

    vw_export_entities -v <VW Appliance IP> -u <Username> {-p <Password>|-z <Password File>} {-e <Entity Search String>|-t <Entity Type>} [-o <Output File>] [--properties] [--exactonly]

### CSV export of topology for a given entity name / entity id.

Usage:

    vw_show_topology -v <VW Appliance IP> -u <Username> {-p <Password>|-z <Password File>} -e <Entity Search String> [-o <Output File>]

### Create an application defined as Initiator:Target from an application defined as a set of hosts.

Usage:

    vw_expand_app_to_initiator_target -v <VW Appliance IP> -u <Username> {-p <Password>|-z <Password File>} {-a <Application>|-e <Host>[,<Host>][,<Host>]} [-o <Output File>]

| Notation | Description |
| -------- | ----------- |
| Text without brackets or braces | Items you must type as shown |
| <Text inside angle brackets> | Placeholder for which you must supply a value |
| [Text inside square brackets] | Optional items |
| {Text inside braces} | Set of required items; choose one |
| Vertical bar (&#124;) | Separator for mutually exclusive items; choose one |
| Ellipsis (...) | Items that can be repeated |
