"""
Implements a Ryobi Garage Door Opener from their API
"""

import asyncio
import json
import logging
from helpers.constants import HTTP_ENDPOINT
import http_api
import ws_api

_LOGGER = logging.getLogger(__name__)

class RyobiGDO:
    def __init__(self, id, auth):
        _LOGGER.debug("Creating RyobiGDO object.")
        self.auth = auth
        self.device_id = id
        self.ws = None
        self.wsState = None

        self.name = None
        self.description = None
        self.version = None
        self.lastSeen = None
        self.lastUpdate = None
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
        
        if self.auth is not None and self.device_id is not None:
            self.update_device()
        
    def process_ws_msg(self, topic, data, error=None): 
        _LOGGER.debug("Processing incoming %s: %s", topic, data)

        if topic is ws_api.SIGNAL_CONNECTION_STATE: #Websocket state update
            self.wsState = data
            if error is not None: #is state error update
                _LOGGER.error("Relaying RyobiWebsocket %s: %s", data, error)
                return True
            
            _LOGGER.info("Relaying RyobiWebsocket State: %s", data)
            return True
        
        #If not state update then its a message from the websocket, process below
        msgType = data["method"]
        msgDevice = data["params"]["varName"]

        if msgType == "wskAttributeUpdateNtfy":
            msgTopic = list(data["params"].keys())[2]
            _LOGGER.debug("Processing notification update for %s", msgTopic)
            msgSplit = msgTopic.partition(".")
            moduleName = msgSplit[0]
            moduleUpdate = msgSplit[1]
            
            if moduleName == "garageLight_4":
                msgUpdate = data["params"][msgTopic]
                self.garageLight["lightState"] = msgUpdate["value"]
                self.lastUpdate = msgUpdate["lastSet"]
                return True

        #other msgTypes process here. If not error below

        _LOGGER.error("Could not process RyobiWebsocket message. Unrecognized type: %s. Data: %s", msgType, data)
        return False

    def update_device(self):
        if self.device_id is None: #Don't think this is actually needed.
            _LOGGER.error("No device_id exists or was given to update")
            return False

        _LOGGER.info("Updating device info...")

        response = http_api.get_device(self.auth, self.device_id)
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

    def connectWS(self):
        self.ws = ws_api.RyobiWebsocket(self.process_ws_msg, self.auth, self.device_id)
        loop = asyncio.get_event_loop()
        # loop.create_task(do_other())
        loop.run_until_complete(self.ws.listen())

    def turn_on_light(self, force=False):
        if self.garageLight["lightState"] == True and not force:
            _LOGGER.debug("Light already on. No request sent.")
            return

        _LOGGER.info("Sending Turn on Light command.")
        self.ws.send_command("lightState", "true")

    def turn_off_light(self, force=False):
        if self.garageLight["lightState"] == False and not force:
            _LOGGER.debug("Light already off. No request sent.")
            return True

        _LOGGER.info("Sending Turn off Light command.")
        self.ws.send_command("lightState", "false")

    def open_door(self, force=False):
        if self.garageDoor["doorState"]["state"] == "Open" and not force:
            _LOGGER.info("Door state already open. No request sent.")
            return True
        
        _LOGGER.info("Sending Open Garage Door command.")
        self.ws.send_command("doorCommand", "1")

    def close_door(self, force=False):
        if self.garageDoor["doorState"]["state"] == "Closed" and not force:
            _LOGGER.info("Door state already closed. No request sent.")
            return True

        _LOGGER.info("Sending Close Garage Door command.")
        self.ws.send_command("doorCommand", "0")

    def set_height(self, force=False):
        pass

    def set_vacation_mode(self, mode=False, force=False):
        if self.vacation_mode == mode:
            _LOGGER.info(f"Vacation mode already set to {mode}.")
            return True

        pass

class DeviceResponseError(Exception):
    """Class to throw failed device update response exception."""

class UpdateUnrecognized(Exception):
    """Class to throw failed device update response exception."""
