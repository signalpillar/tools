
# local
from vw.api import core

# 3rd-party
import pytest


class TestApiError:

    def should_parse_error_to_exception(self):
        exception = core.ApiError.from_error_document(
            {
                'code': 'EM.5011',
                'causes': [
                    {'code': '',
                     'causes': [],
                     'data': '',
                     'message': 'Node 1406658900 was not found in the database'}],
                'data': '',
                'message': 'Failed to get properties'
            }
        )
        assert 'EM.5011' == exception.code
        assert (
            'Failed to get properties; Node 1406658900 was not found in the database'
            == exception.message
        )


class TestClient:

    def should_return_data_from_ok_result(self):
        assert ['a', 'b'] == core.Client.parse_api_response({
            "status": "OK",
            "result": dict(
                totalCount=2,
                data=["a", "b"]
            )})

    def should_return_result_from_ok_response(self):
        assert "14b71c33-b5c1-4351-8777-6f969ef0d5f2" == core.Client.parse_api_response({
            "status": "OK",
            "result": "14b71c33-b5c1-4351-8777-6f969ef0d5f2"
        })

    def should_raise_error_from_failed_response(self):
        with pytest.raises(core.OperationFailure):
            core.Client.parse_api_response({
                'status': 'Failure',
                'error': {
                    'message': 'Report is not requested.',
                    'data': None,
                    'causes': [],
                    'code': 'RC.5001'
                }})
