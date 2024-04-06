import js
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch
from datetime import datetime

document = js.document

latestBlog = [
    [document.getElementById("latestBlog1"), document.getElementById("latestAuthor1"), document.getElementById("latestDate1")],
    [document.getElementById("latestBlog2"), document.getElementById("latestAuthor2"), document.getElementById("latestDate2")],
    [document.getElementById("latestBlog3"), document.getElementById("latestAuthor3"), document.getElementById("latestDate3")]
             ]

mostLikedBlog = [
    [document.getElementById("mostLikedBlog1"), document.getElementById("mostLikedAuthor1"), document.getElementById("mostLikedDate1")],
    [document.getElementById("mostLikedBlog2"), document.getElementById("mostLikedAuthor2"), document.getElementById("mostLikedDate2")],
    [document.getElementById("mostLikedBlog3"), document.getElementById("mostLikedAuthor3"), document.getElementById("mostLikedDate3")]
             ]

async def getCurrentBlogID():
    try:
        response = await pyfetch(
            url=f"/getCurrentBlogID/", 
            method='GET',
            headers={'Content-Type': 'application/json'}
        )
        if response.ok:
            data = await response.json()
            return data
    except Exception as e:
        print(e)

async def loadBlog(index):
    try:
        response = await pyfetch(
            url=f"/getBlog/?blogID={index}", 
            method='GET',
            headers={'Content-Type': 'application/json'}
        )
        if response.ok:
            data = await response.json()
            return data
    except Exception as e:
        print(e)

async def getUserDetail(userID):
    try:
        response = await pyfetch(
            url=f"/user/getUser?userId={userID}", 
            method='GET',
            headers={'Content-Type': 'application/json'}
        )
        if response.ok:
            data = await response.json()
            return data
    except Exception as e:
        print(e) 

async def getMostLikedBlog():
    try:
        response = await pyfetch(
            url=f"/getSortedBlogByLike/", 
            method='GET',
            headers={'Content-Type': 'application/json'}
        )
        if response.ok:
            data = await response.json()
            return data
    except Exception as e:
        print(e)

from textwrap import dedent
import json
import js 
from pyodide.ffi import create_proxy, to_js

window = js.window
document = js.document
location = js.document.location

from math import radians, sin, cos, sqrt, atan2

def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    R = 6371.0
    distance = R * c
    
    return distance

async def success(pos):
    coordinates = pos.coords
    nearby = await getNearby(coordinates.latitude, coordinates.longitude)
    nearby_container = document.getElementById("nearby_list")
    for i in range(len(nearby.get("results"))):
        templeData = document.createElement("div")
        templeData.classList.add("temple__data")
        
        temple = document.createElement("div")
        temple.className = "temple"
        distance_away = haversine_distance(coordinates.latitude, coordinates.longitude, nearby.get("results")[i].get("geometry").get("location").get("lat"), nearby.get("results")[i].get("geometry").get("location").get("lng"))
        temple.innerHTML = nearby.get("results")[i].get("name") + "<br>" + str(round(distance_away, 2)) + " km away, " + nearby.get("results")[i].get("vicinity")
        
        temple_icon = document.createElement("img")
        temple_icon.className  = "temple_icon"
        temple_icon.alt = "temple_icon"
        temple_icon.src = nearby.get("results")[i].get("icon")
        
        templeData.appendChild(temple_icon)
        templeData.appendChild(temple)
        
        nearby_container.appendChild(templeData)
        
def get_current_position(success, error = None, options = None):
    if not options:
        options = {
          "enableHighAccuracy": True,
          "timeout": 5000,
          "maximumAge": 0
        }
    if not error:
        err_msg = dedent('''Oh No! Something happened :(''')
        error = create_proxy(lambda err: print(err_msg.format(err)))
    js.window.navigator.geolocation.getCurrentPosition(create_proxy(success), create_proxy(error), options)

async def getNearby(lat, lon):
    try:
        response = await pyfetch(
            url=f"/nearbyTemple?lat={lat}&lon={lon}", 
            method='get',
            headers={'Content-Type': 'application/json'}
        )
        if response.ok:
            data = await response.json()
            return data
    except Exception as e:
        print(e) 

async def main():
    current_blog_id = await getCurrentBlogID()
    if current_blog_id:
        current_blog_id = current_blog_id["currentBlogID"]
        count = 0
        while count < 3 and current_blog_id > 0:
            current_blog_id -= 1
            blog_data = await loadBlog(current_blog_id)
            if not blog_data.get("detail"):
                if blog_data:
                    username = await getUserDetail(blog_data["author"])
                    
                    latestBlog[count][0].innerText = blog_data["text"]
                    latestBlog[count][1].innerText = username.get("username")
                    latestBlog[count][2].innerText = datetime.fromisoformat(blog_data["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                    count += 1
                
    popular_blog_id = await getMostLikedBlog()
    if popular_blog_id:
        for i in range(min(3, len(popular_blog_id))):
            blog_data = await loadBlog(popular_blog_id[i])
            if not blog_data.get("detail"):
                if blog_data:
                    username = await getUserDetail(blog_data["author"])
                    mostLikedBlog[i][0].innerText = blog_data["text"]
                    mostLikedBlog[i][1].innerText = username.get("username")
                    mostLikedBlog[i][2].innerText = datetime.fromisoformat(blog_data["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
    
    get_current_position(success)

import asyncio
asyncio.ensure_future(main())
