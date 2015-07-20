# std
import argparse

# 3rd-party
import requests


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
        :rtype: :class:`vw.api.Client`
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
                                  "Logged into VirtualWisdom but session check was unsuccessful: {}"
                                  .format(r.content))
        raise ClientError(r.status_code,
                          "Unable to connect to VW with provided information: {}".format(r.content))

    @classmethod
    def parse_api_response(cls, document):
        status = document.get('status')
        if status == 'OK':
            return document.get('result')
        error = document.get('error')
        raise OperationFailure(error.get('code'), error.get('message'))

    def get(self, entrypoint, *args, **kwargs):
        """
        :raise :class:`OperationFailure`: Failed to get resource.
        """
        url = "{}/{}".format(self._api_url, entrypoint)
        response = self._session.get(url, *args, **kwargs)
        if response.status_code == 200:
            json_ = response.json()
            status = json_.get('status')
            if status == 'OK':
                return json_.get('result')
            elif status == 'Failure':
                error = json_.get('error')
                raise OperationFailure(error.get('code'), error.get('message'))

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
            self.__class__.__name,
            self.code,
            self.message)


class OperationFailure(ApiError):
    """API operation failed."""


class Api(object):
    """Base class for different API implementations to declare common state."""

    def __init__(self, client):
        """
        :type client: :class:`vw.api.Client`
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
    :rtype: :class:`vw.api.Client`
    """
    return Client.authenticate(args.host, args.username, args.password or args.passwordfile)
