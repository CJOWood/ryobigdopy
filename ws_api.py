"""Implements known ryobigdo Websocket commands."""

import json
import logging
import traceback
from json import dumps
from helpers.constants import WS_ENDPOINT, WS_MAXRETRY
import websockets

_LOGGER = logging.getLogger(__name__)

SIGNAL_CONNECTION_STATE = "ryobiwebsocket_state" #Callback signal state update
SIGNAL_WEBSOCKET_MESSAGE = "ryobiwebsocket_message" #Callback websocket message

STATE_NOT_STARTED = "not_started" #Represents a state where the socket hasn't attempted to start.
STATE_STARTING = "starting" #Represents a state where the socket is in the process of becoming STATE_CONNECTED
STATE_CONNECTED = "connected" #Represents a state where the socket is connected, authenticated, and subscribed.
STATE_STOPPED = "stopped" #Represents a state where the socket was intentionally stopped, sometimes as a result of MAX_FAILED_ATTEMPTS.
STATE_CLOSED = "closed" #Represents a state where the socket was closed by the server (sometimes due to a connection error)
STATE_ERROR = "error" #Represents a state where the socket/api encountered an error. Should retry connection.

class RyobiWebsocket:

    def __init__(self, callback, auth, device_id):
        self.conn = None
        self.callback = callback
        self.auth = auth
        self.device_id = device_id
        self._is_auth = False
        self._is_notify = False
        self._error_reason = None
        self.state = STATE_NOT_STARTED
        self.failed_attempts = None

    @property
    def state(self):
        """Return the current state."""
        return self._state

    @state.setter
    def state(self, value):
        """Set the state."""
        _LOGGER.debug("Websocket state: %s", value)
        self._state = value
        self.callback(SIGNAL_CONNECTION_STATE, value, self._error_reason)
        self._error_reason = None

    async def running(self):
        try:
            self.state = STATE_STARTING
            _LOGGER.info("Starting websocket connection...")
            async for self.conn in websockets.connect(WS_ENDPOINT):
                if self.failed_attempts > WS_MAXRETRY:
                    _LOGGER.debug("Connection stopped after too many retries (%s).", self.failed_attempts)
                    self._error_reason = f"Connection stopped after too many retries (%s).", self.failed_attempts
                    self.state = STATE_STOPPED
                    break

                try:
                    _LOGGER.debug("is Auth: %s. is Notify: %s", self._is_auth, self._is_notify)
                    if self._is_auth is False:
                        if not await self.send_auth_message():
                            raise WebsocketConnectionError("Authentication failed.")

                    if self._is_notify is False:
                        if not await self.send_subscribe_message():
                            raise WebsocketConnectionError("Subscribing to updates failed.")

                    _LOGGER.info("Websocket connected, authenticated, and subscribed to device.")
                    self.state = STATE_CONNECTED

                    while True:
                        async for message in self.conn:
                            _LOGGER.debug("Message: %s", message)
                            self.callback(SIGNAL_WEBSOCKET_MESSAGE, json.loads(message))
                            #process message
                        if self.state is STATE_STOPPED:
                            _LOGGER.info("Closing websocket...")
                            await self.conn.close()
                            break

                except websockets.ConnectionClosed:
                    _LOGGER.warning("Websocket connection closed. Retrying... %s", self.failed_attempts)
                    self.state = STATE_CLOSED
                    self.failed_attempts += 1
                    self._is_notify = False
                    self._is_auth = False
                    continue

                except WebsocketConnectionError as error:
                    _LOGGER.warning("Failed to authenticate or subscribe. Retrying... %s", self.failed_attempts)
                    self._error_reason = error
                    self.state = STATE_ERROR
                    self.failed_attempts += 1
                    self._is_notify = False
                    self._is_auth = False
                    continue

        except Exception as error:
            def get_traceback(e):
                return ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            _LOGGER.error("Unhandled exception occured: %s", get_traceback(error))
            self.failed_attempts += 1
            self._error_reason = error
            self.state = STATE_ERROR
            self._is_notify = False
            self._is_auth = False

    async def send_auth_message(self):
        _LOGGER.debug("Sending Authentication message.")
        await self.conn.send(json.dumps(
            {'jsonrpc': '2.0',
            'id': 3,
            'method': 'srvWebSocketAuth',
            'params': {
                'varName': self.auth.username,
                'apiKey': self.auth.api_key
                }
            }))
        _LOGGER.debug("Throw away first reply: %s", await self.conn.recv()) #Throw away first reply
        auth_response = json.loads(await self.conn.recv())
        _LOGGER.debug("Recieving after auth: %s", auth_response)
        if auth_response["result"]["authorized"] is True:
            _LOGGER.info("User authenticated successfully.")
            self._is_auth = True
            return True
        return False
    #'{"jsonrpc":"2.0","result":{"authorized":true,"varName":"USER@NAME","aCnt":0},"id":3}'
    
    async def send_subscribe_message(self):
        _LOGGER.debug("Sending Subscribe message.")
        await self.conn.send(json.dumps(
            {'jsonrpc': '2.0',
            'id': 3,
            'method': 'wskSubscribe',
            'params': {
                "topic": f"{self.device_id}.wskAttributeUpdateNtfy"
                }
            }))
        notify_response = json.loads(await self.conn.recv())
        _LOGGER.debug("Recieving after subscribe: %s", notify_response)
        if notify_response["result"]["result"] == "OK":
            _LOGGER.info("User subscribed successfully.")
            self._is_notify = True
            return True
        return False
    #{'jsonrpc': '2.0', 'result': {'result': 'OK', 'aCnt': 0}, 'id': 3}

    async def send_msg(self, msg):
        if self.state is STATE_CONNECTED:
            await self.conn.send(msg)
            return True
        else:
            return False

    async def send_command(self, command, value):
        if self.state is STATE_CONNECTED:
            await self.conn.send(json.dumps(
                {'jsonrpc': '2.0',
                'method': 'gdoModuleCommand',
                'params':
                    {'msgType': 16,
                    'moduleType': 5,
                    'portId': 7, #check if protId same for light/door/modules.
                    'moduleMsg': 
                        {command: value},
                    'topic': self.device_id}
                }))
        #probably check that it worked? Maybe use some kind of Queue that waits for a response and checks against expected otherwise callback? Could revamp sendauth/sendnotify.

    async def listen(self):
        self.failed_attempts = 0
        while self.state != STATE_STOPPED:
            if self.failed_attempts > WS_MAXRETRY:
                self.state = STATE_STOPPED
                break

            await self.running()

        _LOGGER.info("Websocket loop stopped.")

    def close(self):
        """Close the listening websocket."""
        self.state = STATE_STOPPED

class WebsocketConnectionError(Exception):
    """Class to throw an unauthorized access error."""