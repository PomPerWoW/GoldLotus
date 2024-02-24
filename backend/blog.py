from fastapi import APIRouter
from fastapi import Request, Response, Cookie
from datetime import datetime
import sys
import os

router = APIRouter()

PARENT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(1, os.path.join(PARENT_DIRECTORY, "data"))

from content import Blog, Reply, Event
from database import *
from auth.auth_handler import decodeJWT

@router.post("/createBlog/", tags=["blog"])
async def createBlog(response: Response, request: Request, title: str, text: str, media: list, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.blog[root.config["currentBlogID"]] = Blog(root.config["currentBlogID"], title, userId, text, media)
        root.user[userId].createBlog(root.config["currentBlogID"])
        
        root.config["currentBlogID"] += 1
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}

@router.post("/removeBlog/")
async def removeBlog(response: Response, request: Request, blogID: str, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        if not root.user[userId].deleteBlog(blogID):
            raise Exception("user has no permission")
        
        del root.blog[blogID]
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/editBlog/")
async def editBlog(response: Response, request: Request, blogID: str, title: str, text: str, media: list, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        if root.user[userId].editBlog(blogID):
            raise Exception("user has no permission")
        
        root.blog[blogID].editContent(title, text, media)
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}
