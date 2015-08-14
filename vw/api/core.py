"""
vw.api.core
-----------

Module defines two concepts to work with VW HTTP API.

- :class:`Client` - Implements basic HTTP verbs considerign document format for API responses.
    Client raises errors of type :class:`ClientError`

- :class:`Api`    - Base class for any API implementation, has access to the client.
    API implementations raises also own errors of base type :class:`ApiError`.

"""
# std
import argparse

# 3rd-party
import requests

# FIXME: ensure that disabled per client if configured - not globally.
requests.packages.urllib3.disable_warnings()


class BaseError(Exception):
    "Base VW application error."


class ClientError(BaseError):
    """Error raised by client."""


class Client(object):

    def __init__(self, session, api_url):
        """
        :type session: requests.Session
        :type api_url: str
        """
        self._session = session
        self._api_url = api_url

    @classmethod
    def authenticate(cls, hostname, username, password):
        """Factory method to create a authenticated client instance.

        Note::
            `sec` is an undocumented and unsupported API, subject to change in every release

        :type hostname: str
        :type username: str
        :type password: str
        :rtype: :class:`Client`
        :raise :class:`ClientError`: Logged into VW but session check was unsuccessful.
        :raise :class:`ClientError`: Unable to connect to VW with provided information.
        """
        payload = {'username': username, 'password': password, 'targetRoute': None}
        s = requests.Session()
        api_url = 'https://{0}/api/'.format(hostname)
        r = s.post('{}sec/login'.format(api_url), verify=False, data=payload)
        if r.status_code == 200:
            r = s.get('{}sec/session'.format(api_url), verify=False)
            if r.status_code == 200:
                cls.parse_api_response(r.json())
                return cls(s, api_url)
            else:
                raise ClientError(r.status_code,
                                  "Logged into VW but session check was unsuccessful: {}"
                                  .format(r.content))
        raise ClientError(r.status_code,
                          "Unable to connect to VW with provided information: {}".format(r.content))

    @classmethod
    def parse_api_response(cls, document):
        """Parse API response document.

        Successful response document structure::

            {
                "result": {...},
                "status": 'OK'
            }

        Failed response document structure::

            {
                'status': 'Failure',
                'error': {
                    'message': str,
                    'data': ...,
                    'causes': [],
                    'code': str
                }
            }

        :param dict document: API JSON document.
        :return: Value enclosed in `result` or in `data`.
        :raise :class:`vw.api.core.OperationFailure`: API call failed.
        """
        status = document.get('status')
        if status == 'OK':
            result = document.get('result')
            if 'totalCount' in result:
                result = result.get('data')
            return result
        raise OperationFailure.from_error_document(document.get('error'))

    def get(self, entrypoint, *args, **kwargs):
        """
        :type entrypoint: str
        :raise :class:`OperationFailure`: API call resulted error.
        :raise :class:`ClientError`: Failed to call GET method.
        """
        url = "{}/{}".format(self._api_url, entrypoint)
        response = self._session.get(url, *args, **kwargs)
        if response.status_code == 200:
            return self.parse_api_response(response.json())
        raise ClientError(response.status_code, "Failed to call GET method: {}".format(response.content))

    def put(self, entrypoint, expected_status_code, *args, **kwargs):
        """
        :type entrypoint: str
        :type expected_status_code: int
        :raise :class:`OperationFailure`: API call resulted error.
        :raise :class:`ClientError`: Failed to call PUT method.
        """
        url = "{}/{}".format(self._api_url, entrypoint)
        response = self._session.put(url, *args, **kwargs)
        if response.status_code == expected_status_code:
            return self.parse_api_response(response.json())
        raise ClientError(response.status_code, "Failed to call PUT method: {}".format(response.content))

    def __getattr__(self, name):
        return getattr(self._session, name)


class ApiError(BaseError):
    """API related errors."""

    def __init__(self, code, message):
        super(ApiError, self).__init__(message)
        self.code = code
        self.message = message

    def __repr__(self):
        return "{class_}({code!r}, {message!r}".format(
            self.__class__.__name__,
            self.code,
            self.message)

    @classmethod
    def from_error_document(cls, document):
        """Parse error document to exception instance.

        Error document example::

            {
                'code': 'EM.5011',
                'causes': [{'code': '', 'causes': [], 'data': '', 'message': 'Node 1406658900 was not found in the database'}],
                'data': '',
                'message': 'Failed to get properties'
            }

        :param dict document: Error document.
        :rtype: :class:`ApiError`
        """
        code = document.get('code')
        message = document.get('message')
        causes = '; '.join(
            cause_dict.get('message')
            for cause_dict in document.get('causes')
        )
        return cls(code, message="{}; {}".format(message, causes))


class OperationFailure(ApiError):
    """API operation failed."""


class Api(object):
    """Base class for different API implementations to declare common state."""

    def __init__(self, client):
        """
        :type client: :class:`Client`
        """
        self._client = client


def create_api_client_cli_parser():
    """Create a parent parser to bring API client command line arguments.

    :rtype: argparse.ArgumentParser
    """

    def read_password_from_file(path):
        with open(path, 't') as fd:
            return next(fd).strip()

    parser = argparse.ArgumentParser(
        description='VW API authentication options.',
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        # Use the "resolve" conflict_handler because there might be
        # previous options specified with the same name.
        conflict_handler="resolve"
    )
    parser.add_argument("-v", "--virtualwisdom", dest="host", help="Appliance address")
    parser.add_argument("-u", "--username", dest="username", help="API username")
    parser.add_argument("-p", "--password", dest="password", help="API password")
    parser.add_argument("-z", "--password-file", type=read_password_from_file, dest="passwordfile",
                        help="Path to the password-file, where first line should be a password "
                             "(trailing spaces are truncated).")
    return parser


def create_api_client(args):
    """Create an API client from parsed CLI arguments (see :func:`create_api_client_cli_parser`)

    :type args: argparse.Namespace
    :rtype: :class:`Client`
    """
    return Client.authenticate(args.host, args.username, args.password or args.passwordfile)
