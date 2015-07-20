"""
Use cases:

- Metric trend data case: input (starttime-endtime, entry name and metric name). Entry name would need to be resolved to an entityuuid using GetEntityId() from ShowTopology.py .  then it would make a call to reportBatch with some uuid (i think we can just make one up) and the information from above .. then it will return OK and the uuid provided above .. then the script needs to call reportPoll with the uuid to check on the status and get the data back ..

- Separate cases for the user to request a "top x", they would provide an entity type instead of an entity and the script would retrieve a list of entities and their summaries

- Final(?) case is if the user provides a histogram metric we would be retrieving the histogram bin information instead of a time series trend
"""

# std
import argparse
import sys

# local
from vw.api.core import create_api_client_cli_parser, create_api_client


def main():

    def create_parser(parents):
        parser = argparse.ArgumentParser(
            description='Export metric trend data.',
            parents=parents,
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument("-e", "--entity", action="store", dest="entity", help="Entity name")
        parser.add_argument("-m", "--metric", action="store", dest="metric", help="Metric name")
        parser.add_argument("--starttime", action="store", dest="starttime")
        parser.add_argument("--endtime", action="store", dest="endtime")
        return parser

    parser = create_parser([create_api_client_cli_parser()])
    args = parser.parse_args(sys.argv[1:])
    client = create_api_client(args)
    print(client)
