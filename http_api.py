"""Implements known ryobigdo HTTP API calls."""

import logging
from json import dumps
from urllib import response
from helpers.constants import HTTP_ENDPOINT, RYOBI_URL, HTTP_TIMEOUT
from requests import Request, exceptions
from urllib3.util.retry import Retry

_LOGGER = logging.getLogger(__name__)

def get_devices(auth):
    url = f"{HTTP_ENDPOINT}/devices"
    headers = {
        "Host": RYOBI_URL,
        "Content-Type": "application/json",
    }
    data = dumps(
        {
            "username": auth.username,
            "password": auth.password,
        }
    )
    return query(
        auth,
        url=url,
        reqtype="get",
        data=data,
        headers=headers
    )

def get_device(auth, url, device_id):
    headers = {
        "Host": RYOBI_URL,
        "Content-Type": "application/json",
    }
    data = dumps(
        {
            "username": auth.username,
            "password": auth.password,
        }
    )

    return query(
        auth,
        url=f"{url}/{device_id}",
        reqtype="get",
        data=data,
        headers=headers
    )

def request_login(
    auth,
    url,
    login_data,
):
    """
    Login request.
    :param auth: Auth instance.
    :param url: Login url.
    :login_data: Dictionary containing ryobi login data.
    """
    headers = {
        "Host": RYOBI_URL,
        "Content-Type": "application/json",
    }
    data = dumps(
        {
            "username": login_data["username"],
            "password": login_data["password"],
        }
    )

    return query(
        auth,
        url=url,
        headers=headers,
        data=data,
        json_resp=False,
        reqtype="post",
    )

def prepare_request(url, headers, data, reqtype):
        """Prepare a request."""
        r = Request(reqtype.upper(), url, headers=headers, data=data)
        return r.prepare()

def query(
        auth,
        url=None,
        data=None,
        headers=None,
        reqtype="get",
        stream=False,
        json_resp=True,
        timeout=HTTP_TIMEOUT,
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
        req = prepare_request(url, headers, data, reqtype)
        try:
            response = auth.session.send(req, stream=stream, timeout=timeout)
            return response
        except (exceptions.ConnectionError, exceptions.Timeout):
            _LOGGER.error(
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
            _LOGGER.error(
                "Expected json response from %s, but received: %s: %s",
                url,
                code,
                reason,
            )
        return None

class RyobiBadResponse(Exception):
    """Class to throw bad json response exception."""

class UnauthorizedError(Exception):
    """Class to throw an unauthorized access error."""