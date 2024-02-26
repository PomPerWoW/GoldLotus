from typing import List
from fastapi import APIRouter
from fastapi import Request, Response, Cookie
from datetime import date, datetime
import sys
import os

router = APIRouter()

PARENT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(1, os.path.join(PARENT_DIRECTORY, "data"))

from content import Reply, Event
from database import *
from auth.auth_handler import decodeJWT

@router.post("/createEvent/", tags=["event"])
async def createEvent(response: Response, request: Request, title: str, text: str, media: List[str], date: datetime, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.event[root.config["currentEventID"]] = Event(root.config["currentEventID"], title, userId, text, media, date)
        root.user[userId].createEvent(root.config["currentEventID"])
        
        root.config["currentEventID"] += 1
        
        transaction.commit()
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
        
        del root.event[eventID]
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/editEvent/")
async def editEvent(response: Response, request: Request, eventID: int, title: str, text: str, media: List[str], date: datetime, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        if root.user[userId].editEvent(eventID):
            raise Exception("user has no permission")
        
        root.event[eventID].editContent(title, text, media, date)
        
        transaction.commit()
    except Exception as e:
        return {"detail": str(e)}

@router.post("/addReplyEvent/")
async def addReplyEvent(response: Response, request: Request, eventID: int, text: str, media: List[str], access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        root.event[eventID].addReply(userId, text, media)
        
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