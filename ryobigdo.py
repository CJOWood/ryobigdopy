"""
Implements a Ryobi Garage Door Opener from their API
"""

from distutils.command.build_scripts import first_line_re
import json
import logging
from xmlrpc.client import ResponseError
from helpers.constants import HTTP_ENDPOINT
import http_api

_LOGGER = logging.getLogger(__name__)

class RyobiGDO:
    def __init__(self, id, auth):
        _LOGGER.debug("Creating RyobiGDO object.")
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
            _LOGGER.error("No device_id exists or was given to update")
            return False

        response = http_api.get_device(self.auth, f"{HTTP_ENDPOINT}/devices", self.device_id)
        try:
            if response.status_code == 200:
                self.device_response = response.json()
                self.extract_device_info()
                return response.json()
            raise DeviceResponseError
        except AttributeError as error:
            raise DeviceResponseError from error

    def extract_device_info(self):
        if self.device_response is None:
            _LOGGER.error("Variable device_response is empty. Cannot extract info.")
            raise AttributeError("No response info available to extract!")

        first_result = self.device_response["result"][0]
        garageDoor = first_result["deviceTypeMap"]["garageDoor_4"]["at"]
        garageLight = first_result["deviceTypeMap"]["garageLight_4"]["at"]

        self.name = first_result["metaData"]["name"]
        self.description = first_result["metaData"]["description"]
        self.version = first_result["metaData"]["version"]
        self.lastSeen = first_result["metaData"]["sys"]["lastSeen"]
        self.serial = first_result["deviceTypeMap"]["masterUnit"]["at"]["serialNumber"]["value"]
        self.mac = first_result["deviceTypeMap"]["masterUnit"]["at"]["macAddress"]["value"]
        self.wifiVersion = first_result["deviceTypeMap"]["masterUnit"]["at"]["appVersion"]["value"]
        self.garageDoor = {
            "vacationMode": garageDoor["vacationMode"]["value"],
            "sensorFlag": {
                "lastSet": garageDoor["sensorFlag"]["lastSet"],
                "lastValue": garageDoor["sensorFlag"]["lastValue"],
                "value": garageDoor["sensorFlag"]["value"],
            },
            "doorState": {
                "lastSet": garageDoor["doorState"]["lastSet"],
                "lastValue": garageDoor["doorState"]["lastValue"],
                "value": garageDoor["doorState"]["value"],
                "enum": garageDoor["doorState"]["enum"],
                "state": garageDoor["doorState"]["enum"][garageDoor["doorState"]["value"]]
            },
            "doorPercentOpen": garageDoor["doorPercentOpen"]["value"],
        }
        self.garageLight = {
            "lightState": garageLight["lightState"]["value"],
            "lightTimer": garageLight["lightTimer"]["value"],
        }
        self.device_response = None
        _LOGGER.info("Device information updated!")
        return True

    def turn_on_light(self):
        if self.garageLight["lightState"] == True:
            return True


    def turn_off_light(self):
        if self.garageLight["lightState"] == False:
            return True

    def open_door(self):
        if self.garageDoor["doorState"]["state"] == "Open":
            _LOGGER.info("Door state already open.")
            return True
        
        pass

    def close_door(self):
        if self.garageDoor["doorState"]["state"] == "Closed":
            _LOGGER.info("Door state already closed.")
            return True

        pass

    def set_height():
        pass

    def set_vacation_mode(self, mode = False):
        if self.vacation_mode == mode:
            _LOGGER.info(f"Vacation mode already set to {mode}.")
            return True

        pass


class DeviceResponseError(Exception):
    """Class to throw failed device update response exception."""
