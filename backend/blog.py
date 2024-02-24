
from fastapi import FastAPI, Request, Response, Cookie
from datetime import datetime
import sys
import os

app = FastAPI()

PARENT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(1, os.path.join(PARENT_DIRECTORY, "data"))

from content import Blog, Reply, Event
from database import *
from auth.auth_handler import decodeJWT

@app.post("/postBlog/")
async def postBlog(response: Response, request: Request, title: str, text: str, media: list, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.blog[root.config["currentBlogID"]] = root.user[userId].createBlog(root.config["currentBlogID"], title, text, media)
        
        root.config["currentBlogID"] += 1
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}

@app.post("/removeBlog/")
async def removeBlog(response: Response, request: Request, blogID: str, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        if not root.user[userId].deleteBlog(blogID):
            raise Exception("user has no permission")    
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}
    
@app.post("/editBlog/")
async def editBlog(response: Response, request: Request, blogID: str, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        if root.user[userId].deleteBlog(blogID):
            raise Exception("user has no permission")    
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}