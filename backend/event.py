
from typing import List
from fastapi import APIRouter, Request, Response, Cookie, UploadFile
from typing import Optional, List
from datetime import datetime
import shutil
import sys
import os

router = APIRouter()

PARENT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(1, os.path.join(PARENT_DIRECTORY, "data"))

from content import Event
from database import *
from auth.auth_handler import decodeJWT

@router.post("/createEvent/", tags=["event"])
async def createEvent(response: Response, request: Request, title: str, text: str, date: datetime, media: Optional[List[UploadFile]] = None, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
            
        mediaID = list()
        if media != None:
            for file in media:
                file_path = os.path.join("uploads", str(root.config["currentMediaID"]) + "." + file.filename.split(".")[-1])
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                mediaID.append(root.config["currentMediaID"])
                root.config["currentMediaID"] += 1
        
        root.event[root.config["currentEventID"]] = Event(root.config["currentEventID"], title, userId, text, mediaID, date)
        root.user[userId].createEvent(root.config["currentEventID"])
        
        root.config["currentEventID"] += 1
        transaction.commit()
        
        return root.eventID[root.config["currentEventID"] - 1]
    except Exception as e:
        return {"detail": str(e)}

@router.post("/removeEvent/")
async def removeEvent(response: Response, request: Request, eventID: str, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        if not root.user[userId].deleteEvent(eventID):
            raise Exception("user has no permission")
        
        event = root.event[eventID]
        for mediaID in event.media:
            if os.path.exists(os.path.join("uploads", str(mediaID)) + ".png"):
                os.remove(os.path.join("uploads", str(mediaID)) + ".png")
            elif os.path.exists(os.path.join("uploads", str(mediaID)) + ".jpg"):
                os.remove(os.path.join("uploads", str(mediaID)) + ".jpg")
            elif os.path.exists(os.path.join("uploads", str(mediaID)) + ".jpeg"):
                os.remove(os.path.join("uploads", str(mediaID)) + ".jpeg")
            elif os.path.exists(os.path.join("uploads", str(mediaID)) + ".MP4"):
                os.remove(os.path.join("uploads", str(mediaID)) + ".MP4")
            else:
                raise Exception("File not found in the db.")
        
        del root.event[eventID]
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/editEvent/")
async def editEvent(response: Response, request: Request, eventID: int, title: str, text: str, date: datetime, media: Optional[List[UploadFile]] = None, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        if root.user[userId].editEvent(eventID):
            raise Exception("user has no permission")
        
        mediaID = list()
        if media == None:
            for current in root.event[eventID].media:
                if os.path.exists(os.path.join("uploads", str(current)) + ".png"):
                    os.remove(os.path.join("uploads", str(current)) + ".png")
                elif os.path.exists(os.path.join("uploads", str(current)) + ".jpg"):
                    os.remove(os.path.join("uploads", str(current)) + ".jpg")
                elif os.path.exists(os.path.join("uploads", str(current)) + ".jpeg"):
                    os.remove(os.path.join("uploads", str(current)) + ".jpeg")
                elif os.path.exists(os.path.join("uploads", str(current)) + ".MP4"):
                    os.remove(os.path.join("uploads", str(current)) + ".MP4")
                else:
                    raise Exception("File not found in the db.")
        else:
            temp = list()
            for file in media:
                filename, file_extension = os.path.splitext(file.filename)
                temp.append(filename)
                
            for current in root.event[eventID].media:
                if not current in temp:
                    if os.path.exists(os.path.join("uploads", str(current)) + ".png"):
                        os.remove(os.path.join("uploads", str(current)) + ".png")
                    elif os.path.exists(os.path.join("uploads", str(current)) + ".jpg"):
                        os.remove(os.path.join("uploads", str(current)) + ".jpg")
                    elif os.path.exists(os.path.join("uploads", str(current)) + ".jpeg"):
                        os.remove(os.path.join("uploads", str(current)) + ".jpeg")
                    elif os.path.exists(os.path.join("uploads", str(current)) + ".MP4"):
                        os.remove(os.path.join("uploads", str(current)) + ".MP4")
                    else:
                        raise Exception("File not found in the db.")
            
            for file in media:
                filename, file_extension = os.path.splitext(file)
                if not filename in root.event[eventID].media:
                    file_path = os.path.join("uploads", str(root.config["currentMediaID"]) + "." + file.filename.split(".")[-1])
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)
                    
                    mediaID.append(root.config["currentMediaID"])
                    root.config["currentMediaID"] += 1
                else:
                    mediaID.append(filename)
        
        root.event[eventID].editContent(title, text, mediaID, date)
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}

@router.post("/addReplyEvent/")
async def addReplyEvent(response: Response, request: Request, eventID: int, text: str, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        root.event[eventID].addReply(userId, text)
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/removeReplyEvent/")
async def addReplyEvent(response: Response, request: Request, eventID: int, replyIndex: str, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        if not root.event[eventID].removeReply(replyIndex, userId):
            raise Exception("user has no permission")
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}

@router.post("/addAttending/")
async def addAttending(response: Response, request: Request, eventID: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.event[eventID].addAttending(userId)
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/removeAttending/")
async def removeAttending(response: Response, request: Request, eventID: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.event[eventID].removeAttending(userId)
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}

@router.post("/addMaybe/")
async def addMaybe(response: Response, request: Request, eventID: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.event[eventID].addMaybe(userId)
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/removeMaybe/")
async def removeMaybe(response: Response, request: Request, eventID: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.event[eventID].removeMaybe(userId)
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}

@router.post("/addNotAttending/")
async def addNotAttending(response: Response, request: Request, eventID: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.event[eventID].addNotAttending(userId)
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/removeNotAttending/")
async def removeNotAttending(response: Response, request: Request, eventID: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.event[eventID].removeNotAttending(userId)
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}