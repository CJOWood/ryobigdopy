# ryobigdopy

Async library to react to events issued over Ryobi GDO Websockets.

## Example use

```python
import auth as a
import ryobigdo
import logging

_LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

creds = {
    "username": RYOBI_USERNAME, #Username from Ryobi GDO App
    "password": RYOBI_PASSWORD, #Password from Ryobi GDO App
    }

auth = a.Auth(creds) #Manages login, creds, and API Key
auth.login() #Checks creds and gets API Key for use in Websocket.

print(http_api.get_devices(auth)) #Choose DEVICE_ID wanted and give to RyobiGDO Obj.

DEVICE_ID = "" #From http_api.get_devices()

gdo = ryobigdo.RyobiGDO(DEVICE_ID, auth)
gdo.connect_ws()
```
