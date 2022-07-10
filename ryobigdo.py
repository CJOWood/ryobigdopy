"""
Implements a Ryobi Garage Door Opener from their API
"""

import logging
from xmlrpc.client import ResponseError
from helpers.constants import HTTP_ENDPOINT
import http_api

_logger = logging.getLogger(__name__)

class RyobiGDO:
    def __init__(self, id, auth):
        self.auth = auth
        self.device_id = id
        self.name = None
        self.description = None
        self.version = None
        self.lastSeen = None
        self.serial = None
        self.mac = None
        self.wifiVersion = None
        self.garageDoor = {
            "vacationMode": None,
            "sensorFlag": {
                "lastSet": None,
                "lastValue": None,
                "value": None,
            },
            "doorState": {
                "lastSet": None,
                "lastValue": None,
                "value": None,
                "enum": ["Closed", "Open", "Closing", "Opening", "Fault"],
            },
            "doorPercentOpen": None,
        }
        self.garageLight = {
            "lightState": None,
            "lightTimer": None,
        }

        self.device_response = None
        """
        if self.auth is not None and self.device_id is not None:
            self.update_device(self, self.auth)
        """

    def update_device(self):
        if self.device_id is None:
            _logger.error("No device_id exists or was given to update")

        response = http_api.get_device(self.auth, f"{HTTP_ENDPOINT}/devices", self.device_id)
        try:
            if response.status_code == 200:
                self.device_response = response.json()
                self.extract_device_info()
                return response.json()
            raise ResponseError
        except AttributeError as error:
            raise ResponseError from error

    def extract_device_info(self):
        self.name = self.device_response["result"][0]["metaData"]["name"]
        self.description = self.device_response["result"][0]["metaData"]["description"]
        return True