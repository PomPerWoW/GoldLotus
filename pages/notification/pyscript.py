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
        
async def removeAllNotification():
    try:
        response = await pyfetch(
            url=f"/user/removeAllNotification", 
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

async def handle_delete_all(_):
    await removeAllNotification()
    container.innerHTML = ""
    
async def display_notification(notifications):
    container.innerHTML = ""
    for i in range(len(notifications)):
            outer = document.createElement("div")
            outer.classList.add("noti--head--box")
            
            noti = document.createElement("div")
            noti.id = f"noti_{i}"
            text = noti.textContent = notifications[i].get("text")  
            if notifications[i].get("status"):
                noti.textContent = text                 # Read
            else:
                noti.innerHTML = f"<b>{text}</b>"       # Unread
            outer.appendChild(noti)
            noti.classList.add("noti--box--name")

            
            rm = document.createElement("a")
            rm.id = f"rm_{i}"
            rm.textContent = "delete"
            add_event_listener(rm, "click", functools.partial(handle_delete, i))
            outer.appendChild(rm)
            rm.classList.add("noti--box--delete")

            
            container.appendChild(outer)

async def main():
    notifications = await getAllNotification()
    if notifications:
        notifications = notifications.get("data")
        await display_notification(notifications)
    
    await markAllNotificationsAsRead()
    
    add_event_listener(document.getElementById("delete_all"), "click", handle_delete_all)
            

import asyncio
asyncio.ensure_future(main())
