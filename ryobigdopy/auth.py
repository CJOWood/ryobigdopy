import logging
import http_api
from functools import partial
from requests import Session
from helpers.constants import (
    HTTP_ENDPOINT,
    WS_ENDPOINT,
    HTTP_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


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
        s.get = partial(s.get, timeout=HTTP_TIMEOUT)
        return s

    def login(self, login_url=f"{HTTP_ENDPOINT}/login"):
        """Attempt login to ryobigdo servers."""
        _LOGGER.info("Attempting login with %s", login_url)
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

class LoginError(Exception):
    """Class to throw failed login exception."""