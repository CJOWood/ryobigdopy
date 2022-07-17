# ryobigdopy

Library to interface with Ryobi GDO Websockets in Python.

## Example use

```python
import auth as a
import ryobigdo

creds = {
    "username": RYOBI_USERNAME, #Username from Ryobi GDO App
    "password": RYOBI_PASSWORD, #Password from Ryobi GDO App
    }

auth = a.Auth(creds) #Manages login, creds, and API Key
auth.login() #Checks creds and gets API Key for use in Websocket.

print(http_api.get_devices(auth).json()) #Choose DEVICE_ID wanted and give to RyobiGDO Obj.

DEVICE_ID = "" #From http_api.get_devices()

gdo = ryobigdo.RyobiGDO(DEVICE_ID, auth)
gdo.connect_ws()
```
