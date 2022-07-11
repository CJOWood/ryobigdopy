"""Implements known ryobigdo Websocket commands."""

import json
import logging
from json import dumps
from helpers.constants import WS_ENDPOINT, WS_TIMEOUT
import asyncio
import websockets

_logger = logging.getLogger(__name__)


class RyobiWebsocket:

    def __init__(self, auth, device_id):
        self._conn = None
        self.auth = auth
        self.device_id = device_id
        self.is_auth = False
        self.is_notify = False

    async def main(self):
        await self.connect()
        loop = asyncio.get_event_loop()
        loop.run_forever(await self.receive())

    async def connect(self):
        self._conn = await websockets.connect(WS_ENDPOINT, timeout=None)
        _logger.debug(await self.send_auth_message(self.auth))
        _logger.debug(await self.send_notify_message())

    async def send(self, message):
        await self._conn.send(message)

    async def receive(self):
        return _logger.debug(await self._conn.recv())

    async def send_auth_message(self, auth):
        return await self._conn.send(json.dumps(
            {'jsonrpc': '2.0',
                'id': 3,
                'method': 'srvWebSocketAuth',
                'params': {
                    'varName': auth.username,
                    'apiKey': auth.api_key}}))
    """'{"jsonrpc":"2.0","result":{"authorized":true,"varName":"chris@chriswood.org","aCnt":0},"id":3}'"""
    
    async def send_notify_message(self):
        return await self._conn.send(json.dumps(
            {'jsonrpc': '2.0',
                'id': 3,
                'method': 'wskSubscribe',
                'params': {
                    "topic": f"{self.device_id}.wskAttributeUpdateNtfy"
                    }
            }))
