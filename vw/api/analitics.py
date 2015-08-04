"""
vw.api.analitics
----------------

- GET  /analytics/metrics            - A call to retrieve all metrics' information. It only returns the metrics which are viewable based on licensing.
- GET  /analytics/dbtimerange        - A call to retrieve all metrics' information. It only returns the metrics which are viewable based on licensing.
- PUT  /analytics/topx               - Returns the TopX chart with the specified query parameters.
- PUT  /analytics/topxTrend          - Returns the TopX trend chart with the specified query parameters.
- PUT  /analytics/topxBox
- PUT  /analytics/topxTable
- GET  /analytics/scsiMessageTypes
- POST /analytics/reportTemplate     - Saves the specified analytics template.
- DEL  /analytics/reportTemplate     -  Delete the report template with the specified ID and revision.
- GET  /analytics/reportTemplateById - Returns an report template with the specified ID.
- GET  /analytics/reportTemplateList - Lists all report templates.
- PUT  /analytics/reportBatch        - Send a batch request for a report. This is an unblocked method. Use {@link #pollReport(String)} or {@link #getReportCharts(String, List)} to get the chart data.
- DEL  /analytics/reportBatch        - This method should be called after the client receives all the reports of the batch request. It releases system resources.
- GET  /analytics/poll/reportPoll    - This method provides a polling mechanism to get the charts of a report. The returned charts will be shown in the following {@link #pollReport(String)} calls.
- GET  /analytics/reportCharts       -  This method explicitly gets specified charts of a report. The returned charts will be shown in the following {@link #pollReport(String)} calls.
- PUT  /analytics/trends             - A call to get trends over time for the given chart request parameters
- PUT  /analytics/histogram          - A call to get the histogram information for a given entity/metric combination
- GET  /dashboard                    - Returns the dashboard of the current user. 
- PUT  /dashboard                    - Set the report as dashboard.
- PUT  /dashboard/setting            - Update autoRotate and/or autoRefresh value if they are present.
- POST /reports/exportReportForImport- Exports a report so that it can be imported into another instance of VW4.
- POST /reports/importReport         - Handles file upload for importing a chart
"""

# std
import itertools
import uuid

# local
from .core import Api


class AnaliticsApi(Api):

    @property
    def templates(self):
        return self._client.get('analytics/analyticsTemplate')

    def create_report_batch(self, entity_type, entity_uuid, metric_name, start_timestamp, end_timestamp):
        """Create batch report.

        :param str entity_type: Type of the entity
        :param str entity_uuid: Unique entity identifier
        :param str metric_name: Metric name
        :param int start_timestamp: Start date as timestamp in milliseconds
        :param int end_timestamp: End date as timestamp in milliseconds
        :return: Report UUID.
        """
        report_data_request_uuid = uuid.uuid4()
        chart_uuid = uuid.uuid4()

        request_body = {
            "uuid": str(report_data_request_uuid),
            "startTimestamp": int(start_timestamp),
            "endTimestamp": int(end_timestamp),
            "charts": [
                {
                    "chartUuid": str(chart_uuid),
                    "chartType": "trend",
                    "chartQueryParams": [
                        {
                            "desiredPoints": 289,
                            "queryParamKey": "{entity_uuid}_{metric_name}_static".format(
                                entity_uuid=entity_uuid,
                                metric_name=metric_name),
                            "entityType": entity_type,
                            "metricName": metric_name,
                            "entity": str(entity_uuid),
                            "filterByEntities": []
                        }
                    ]
                }
            ]

        }
        return self._client.put(
            "analytics/reportBatch",
            expected_status_code=200,
            json=request_body,
            verify=False)

    def get_report_batch_data(self, report_data_request_uuid):
        return self._client.get('analytics/reportPoll', params=dict(uuid=report_data_request_uuid))


def parse_time_points(data):
    """Parse all time points from all charts present in the polled report data.

    Expected input has the following structure::

        {'charts': [
            {'chartData': [
                {'data': [[1436659200000, 0.0],
                          [1436745600000, 0.0],
                          [1438646400000, 0.0]],
                 'queryParamKey': '8a4ce09122ab4046a4302799a3950325_ReadECTMean_static'}],
             'status': 'OK',
             'uuid': '9ebc86b3-8f82-43f1-8474-91ded78d161c'}
         ],
        'finished': True,
        'uuid': '14b71c33-b5c1-4351-8777-6f969ef0d5f2'}

    .. note::

        charts.chartData.data can have `None` value

    :param dict data: Polled batch report data.
    :return: Iterable[list]
    """
    return itertools.chain.from_iterable([
        chart.get('data', [])
        for chart_data in data.get('charts', ())
        for chart in chart_data.get('chartData', ())
    ])
