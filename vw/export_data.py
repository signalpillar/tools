"""
Use cases:

- Metric trend data case: input (starttime-endtime, entry name and metric name). Entry name would need to be resolved to an entityuuid using GetEntityId() from ShowTopology.py .  then it would make a call to reportBatch with some uuid (i think we can just make one up) and the information from above .. then it will return OK and the uuid provided above .. then the script needs to call reportPoll with the uuid to check on the status and get the data back ..

- Separate cases for the user to request a "top x", they would provide an entity type instead of an entity and the script would retrieve a list of entities and their summaries

- Final(?) case is if the user provides a histogram metric we would be retrieving the histogram bin information instead of a time series trend
"""

# std
import argparse
import csv
import io
import sys

# local
from vw.api.core import create_api_client_cli_parser, create_api_client
from vw.api.analitics import AnaliticsApi, parse_time_points
from vw.api.entity import EntityApi


def main():

    args = create_parser([create_api_client_cli_parser()]).parse_args(sys.argv[1:])
    client = create_api_client(args)
    entity_api = EntityApi(client)
    analytics_api = AnaliticsApi(client)

    entities = entity_api.find_entities_by_pattern(args.entity, entity_type=args.entity_type)
    if not entities:
        fail("No entities found by name {_.entity!r}, type {_.entity_type!r}".format(_=args))
    elif len(entities) > 1:
        fail("More than 1 entites found by name {_.entity!r}, type {_.entity_type!r}".format(_=args))
    entity = entities[0]
    report_uuid = analytics_api.create_report_batch(
        args.entity_type,
        entity.get('Id'),
        args.metric,
        args.starttime,
        args.endtime)
    data = analytics_api.get_report_batch_data(report_uuid)
    print(chart_data_to_csv(data, args.report_in_milliseconds))


def chart_data_to_csv(data, report_in_milliseconds, delimiter=','):
    with io.StringIO() as fd:
        writer = csv.writer(fd, delimiter=delimiter)
        data = parse_time_points(data)
        if not report_in_milliseconds:
            data = map(timestamp_to_seconds, data)
        for row in data:
            writer.writerow(row)
        return fd.getvalue()


def timestamp_to_seconds(row):
    row[0] = row[0] / 1000
    return row


def parse_time_to_timestamp(value):
    """Parse date in natural language to timestamp in milliseconds.

    :param str value: Value like "2 days ago", "4 Feb 2015" etc
    :rtype: float
    """
    import parsedatetime
    cal = parsedatetime.Calendar()
    date = cal.parseDT(value)[0]
    return date.timestamp() * 1000


def create_parser(parents):
    parser = argparse.ArgumentParser(
        description='Export metric trend data.',
        parents=parents,
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-e", "--entity", action="store", dest="entity",
                        help="Entity name pattern that may appear in the DisplayLabel or in Tags")
    parser.add_argument("-t", "--entity-type", action="store", dest="entity_type",
                        help="Entity type. For instance, 'Application'")
    parser.add_argument("-m", "--metric", action="store", dest="metric",
                        help="Metric name. For instance, 'ReadECTMean'")
    parser.add_argument("--starttime", action="store", dest="starttime",
                        type=parse_time_to_timestamp,
                        default=parse_time_to_timestamp("10 days ago"),
                        help="Start date (default: 10 days ago)")
    parser.add_argument("--endtime", action="store", dest="endtime",
                        type=parse_time_to_timestamp,
                        default=parse_time_to_timestamp("today"))
    parser.add_argument("--report-in-milliseconds", default=False,
                        dest="report_in_milliseconds",
                        help="If set to True timestamp in report will be in milliseconds not seconds.",
                        action="store_true")
    return parser


def fail(msg):
    print("Error: {}".format(msg), file=sys.stderr)
    sys.exit(1)
