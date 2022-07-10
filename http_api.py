"""Implements known ryobigdo HTTP API calls."""

import logging
from json import dumps
from urllib import response
from helpers.constants import HTTP_ENDPOINT, RYOBI_URL, TIMEOUT

_LOGGER = logging.getLogger(__name__)

def get_devices(auth, url):

    return True

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

    return auth.query(
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

    return auth.query(
        url=url,
        headers=headers,
        data=data,
        json_resp=False,
        reqtype="post",
    )