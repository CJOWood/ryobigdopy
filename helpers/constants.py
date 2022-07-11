"""Generates constants for use in ryobigdopy."""

"""
URLS wss://tti.tiwiconnect.com/api/wsrpc
"""
RYOBI_URL = "tti.tiwiconnect.com"
HTTP_URL = f"https://{RYOBI_URL}"
WS_URL = f"wss://{RYOBI_URL}"
HTTP_ENDPOINT = f"{HTTP_URL}/api"
WS_ENDPOINT = f"{WS_URL}/api/wsrpc"

"""
Dictionaries
"""
ONLINE = {"online": True, "offline": False}

"""
OTHER
"""
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
MIN_THROTTLE_TIME = 2
HTTP_TIMEOUT = 10
WS_TIMEOUT = 3