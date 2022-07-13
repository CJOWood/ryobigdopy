"""Implements known ryobigdo Websocket commands."""

import json
import logging
from json import dumps
from helpers.constants import WS_ENDPOINT, WS_TIMEOUT
import asyncio
import websockets

_LOGGER = logging.getLogger(__name__)

SIGNAL_CONNECTION_STATE = "ryobiwebsocket_state"

STATE_NOT_STARTED = "not_started"
STATE_STARTING = "starting"
STATE_STARTED = "started"
STATE_STOPPED = "stopped"
STATE_ERROR = "error"

class RyobiWebsocket:

    def __init__(self, callback, auth):
        self.conn = None
        self.callback = callback
        self.auth = auth
        self.device_id = None #device_id
        self._is_auth = False
        self._is_notify = False
        self._state = STATE_NOT_STARTED
        self.failed_attempts = None

    @property
    def state(self):
        """Return the current state."""
        return self._state

    @state.setter
    def state(self, value):
        """Set the state."""
        self._state = value
        _LOGGER.debug("Websocket %s", value)
        self.callback(SIGNAL_CONNECTION_STATE, value, self._error_reason)
        self._error_reason = None

    async def running(self):
        try:
            async for self.conn in websockets.connect("wss://ws.postman-echo.com/raw"):
                try:
                    _LOGGER.debug("is Auth: %s. is Notify: %s", self._is_auth, self._is_notify)
                    if self._is_auth is False:
                        await self.send_auth_message()

                    if self._is_notify is False:
                        await self.send_notify_message()

                    while True:
                        async for message in self.conn:
                            _LOGGER.debug("Message: %s", message)
                            self.callback(None, message, None)
                            #process message

                except websockets.ConnectionClosed:
                    continue
        except Exception:
            pass

    async def send_auth_message(self):
        _LOGGER.debug("Sending Authentication message.")
        await self.conn.send(json.dumps(
            {'jsonrpc': '2.0',
                'id': 3,
                'method': 'srvWebSocketAuth',
                'params': {
                    'varName': "auth.username",
                    'apiKey': "auth.apikey"}}))
    #'{"jsonrpc":"2.0","result":{"authorized":true,"varName":"chris@chriswood.org","aCnt":0},"id":3}'
    
    async def send_notify_message(self):
        _LOGGER.debug("Sending Subscribe message.")
        await self.conn.send(json.dumps(
            {'jsonrpc': '2.0',
                'id': 3,
                'method': 'wskSubscribe',
                'params': {
                    "topic": f"DEVICE_IS.wskAttributeUpdateNtfy"
                    }
            }))

    async def send_msg(self, msg):
        if self._state is STATE_STARTED:
            await self.conn.send(msg)

    async def listen(self):
        """Close the listening websocket."""
        self.failed_attempts = 0
        while self.state != STATE_STOPPED:
            await self.running()

    def close(self):
        """Close the listening websocket."""
        self.state = STATE_STOPPED
