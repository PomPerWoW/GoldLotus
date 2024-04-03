
import js
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch

document = js.document

latestBlog1 = document.getElementById("latestBlog1")
latestAuthor1 = document.getElementById("latestAuthor1")
latestDate1 = document.getElementById("latestDate1")

latestBlog2 = document.getElementById("latestBlog2")
latestAuthor2 = document.getElementById("latestAuthor2")
latestDate2 = document.getElementById("latestDate2")

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