import logging
import http_api
from functools import partial
from requests import Request, Session, exceptions
from urllib3.util.retry import Retry
from helpers.constants import (
    HTTP_ENDPOINT,
    WS_ENDPOINT,
    TIMEOUT,
)

_logger = logging.getLogger(__name__)


class Auth:
    """Class to handle login communication."""

    def __init__(self, login_data=None):

        if login_data is None:
            login_data = {}
        self.data = login_data
        self.username = login_data.get("username", None)
        self.password = login_data.get("password", None)
        self.api_key = login_data.get("api_key", None)

        self.login_response = None
        self.is_errored = False

        self.session = self.create_session()

    def create_session(self):
        """Create a session for communication."""
        s = Session()
        s.get = partial(s.get, timeout=TIMEOUT)
        return s
        
    def prepare_request(self, url, headers, data, reqtype):
        """Prepare a request."""
        r = Request(reqtype.upper(), url, headers=headers, data=data)
        return r.prepare()

    def login(self, login_url=f"{HTTP_ENDPOINT}/login"):
        """Attempt login to ryobigdo servers."""
        _logger.info("Attempting login with %s", login_url)
        response = http_api.request_login(
            self,
            login_url,
            self.data,
        )
        try:
            if response.status_code == 200:
                self.login_response = response.json()
                self.extract_info_from_login()
                return response.json()
            raise LoginError
        except AttributeError as error:
            raise LoginError from error

    def extract_info_from_login(self):
        """Extract login info from login response."""
        self.api_key = self.login_response["result"]["auth"]["apiKey"]

    def query(
        self,
        url=None,
        data=None,
        headers=None,
        reqtype="get",
        stream=False,
        json_resp=True,
        timeout=TIMEOUT,
    ):
        """
        Perform server requests.
        :param url: URL to perform request
        :param data: Data to send
        :param headers: Headers to send
        :param reqtype: Can be 'get' or 'post' (default: 'get')
        :param stream: Stream response? True/FALSE
        :param json_resp: Return JSON response? TRUE/False
        """
        req = self.prepare_request(url, headers, data, reqtype)
        try:
            response = self.session.send(req, stream=stream, timeout=timeout)
            return response
        except (exceptions.ConnectionError, exceptions.Timeout):
            _logger.error(
                "Connection error. Endpoint %s possibly down.",
                url,
            )
        except RyobiBadResponse:
            code = None
            reason = None
            try:
                code = response.status_code
                reason = response.reason
            except AttributeError:
                pass
            _logger.error(
                "Expected json response from %s, but received: %s: %s",
                url,
                code,
                reason,
            )
        return None


class LoginError(Exception):
    """Class to throw failed login exception."""


class RyobiBadResponse(Exception):
    """Class to throw bad json response exception."""


class UnauthorizedError(Exception):
    """Class to throw an unauthorized access error."""