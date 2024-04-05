import js
import functools
from pyodide.http import pyfetch
from pyodide.ffi.wrappers import add_event_listener

document = js.document

container = document.getElementById("notifications")

async def getAllNotification():
    try:
        response = await pyfetch(
            url=f"/user/getAllNotification", 
            method='GET',
            headers={'Content-Type': 'application/json'}
        )
        if response.ok:
            data = await response.json()
            return data
    except Exception as e:
        print(e)

async def markAllNotificationsAsRead():
    try:
        response = await pyfetch(
            url=f"/user/markAllNotificationsAsRead", 
            method='POST',
            headers={'Content-Type': 'application/json'}
        )
        if response.ok:
            data = await response.json()
            return data
    except Exception as e:
        print(e)

async def removeNotification(index):
    try:
        response = await pyfetch(
            url=f"/user/removeNotification?index={index}", 
            method='POST',
            headers={'Content-Type': 'application/json'}
        )
        if response.ok:
            data = await response.json()
            return data
    except Exception as e:
        print(e)

async def handle_delete(index, _):
    await removeNotification(index)
    notifications = await getAllNotification()
    if notifications:
        notifications = notifications.get("data")
        await display_notification(notifications)

async def display_notification(notifications):
    container.innerHTML = ""
    for i in range(len(notifications)):
            outer = document.createElement("div")
            
            noti = document.createElement("div")
            noti.id = f"noti_{i}"
            text = noti.textContent = notifications[i].get("text")  
            if notifications[i].get("status"):
                noti.textContent = text                 # Read
            else:
                noti.innerHTML = f"<b>{text}</b>"       # Unread
            outer.appendChild(noti)
            
            rm = document.createElement("a")
            rm.id = f"rm_{i}"
            rm.textContent = "delete"
            add_event_listener(rm, "click", functools.partial(handle_delete, i))
            outer.appendChild(rm)
            
            container.appendChild(outer)

async def main():
    notifications = await getAllNotification()
    if notifications:
        notifications = notifications.get("data")
        await display_notification(notifications)
    
    await markAllNotificationsAsRead()
    
    # add_event_listener(document.getElementById("delete_all"), "click", handle_delete)
            

import asyncio
asyncio.ensure_future(main())
