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

async def main():
    current_blog_id = await getCurrentBlogID()
    if current_blog_id:
        current_blog_id = current_blog_id["currentBlogID"]
        count = 0
        while count < 3 and current_blog_id > 0:
            current_blog_id -= 1
            blog_data = await loadBlog(current_blog_id)
            if blog_data.get("detail"):
                continue
        
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
            if blog_data.get("detail"):
                continue
        
            if blog_data:
                username = await getUserDetail(blog_data["author"])
                
                mostLikedBlog[i][0].innerText = blog_data["text"]
                mostLikedBlog[i][1].innerText = username.get("username")
                mostLikedBlog[i][2].innerText = datetime.fromisoformat(blog_data["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

import asyncio
asyncio.ensure_future(main())
