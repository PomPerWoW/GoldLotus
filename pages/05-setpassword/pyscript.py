import js
from pyscript import window
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch
from pyodide.ffi.wrappers import add_event_listener

document = js.document

async def setPassword(_):
    token = window.location.href[34:]
    password = document.querySelector("#password").value
    try:
        response = await pyfetch(
            url=f"/user/setNewPassword/?token={token}&password={password}", 
            method='POST', 
            headers={'Content-Type': 'application/json'}
        )
        if response.ok:
            data = await response.json()
            if 'detail' in data:
                window.location.href = "/signIn"
            else:
                window.location.href = "/signIn"
    except Exception as e:
        print(e)

add_event_listener(document.getElementById("submit_btn"), "click", setPassword)