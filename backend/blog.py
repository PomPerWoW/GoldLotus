from fastapi import APIRouter
from fastapi import Request, Response, Cookie, File, UploadFile
from datetime import datetime
from typing import List
import shutil
import sys
import os

router = APIRouter()

PARENT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(1, os.path.join(PARENT_DIRECTORY, "data"))

from content import Blog, Reply
from database import *
from auth.auth_handler import decodeJWT

@router.post("/createBlog/", tags=["blog"])
async def createBlog(response: Response, request: Request, title: str, text: str, media: list[UploadFile] = File(...), access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
            
        mediaID = list()
        for file in media:
            file_path = os.path.join("uploads", str(root.config["currentMediaID"]) + "." + file.filename.split(".")[-1])
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            mediaID.append(root.config["currentMediaID"])
            root.config["currentMediaID"] += 1
        
        root.blog[root.config["currentBlogID"]] = Blog(root.config["currentBlogID"], title, userId, text, mediaID)
        root.user[userId].createBlog(root.config["currentBlogID"])
        
        root.config["currentBlogID"] += 1
        transaction.commit()
        
        return root.blog[root.config["currentBlogID"] - 1]
    except Exception as e:
        return {"detail": str(e)}

@router.post("/removeBlog/", tags=["blog"])
async def removeBlog(response: Response, request: Request, blogID: int, access_token: str = Cookie(None)):
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
    
@router.post("/editBlog/", tags=["blog"])
async def editBlog(response: Response, request: Request, blogID: int, title: str, text: str, media: List[str], access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        if not root.user[userId].editBlog(blogID):
            raise Exception("user has no permission")
        
        root.blog[blogID].editContent(title, text, media)
        
        transaction.commit()
        return root.blog[blogID]
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/addLikeBlog/", tags=["blog"])
async def addLikeBlog(response: Response, request: Request, blogID: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        root.blog[blogID].addLike(userId)
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/removeLikeBlog/", tags=["blog"])
async def removeLikeBlog(response: Response, request: Request, blogID: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        root.blog[blogID].removeLike(userId)
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/addReplyBlog/", tags=["blog"])
async def addReplyBlog(response: Response, request: Request, blogID: int, text: str, media: List[str], access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        root.blog[blogID].addReply(userId, text, media)
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/removeReplyBlog/", tags=["blog"])
async def addReplyBlog(response: Response, request: Request, blogID: int, replyIndex: str, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        if not root.blog[blogID].removeReply(replyIndex, userId):
            raise Exception("user has no permission")
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}
    
@router.get("/getBlog/", tags=["blog"])
async def getBlog(response: Response, request: Request, blogID: int):
    try:
        if not blogID in root.blog:
            raise Exception("blog not found")
        
        return root.blog[blogID]
    except Exception as e:
        return {"detail": str(e)}