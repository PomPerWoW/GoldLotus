
from typing import List
from fastapi import APIRouter, File, Request, Response, Cookie, UploadFile
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
async def createEvent(response: Response, request: Request, title: str, text: str, date: datetime, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
            
        mediaID = list()
        
        root.event[root.config["currentEventID"]] = Event(root.config["currentEventID"], title, userId, text, mediaID, date)
        root.user[userId].createEvent(root.config["currentEventID"])
        
        root.config["currentEventID"] += 1
        transaction.commit()
        
        return root.eventID[root.config["currentEventID"] - 1]
    except Exception as e:
        return {"detail": str(e)}

@router.post("/createEventWithMedia/", tags=["event"])
async def createEventWithMedia(response: Response, request: Request, title: str, text: str, date: datetime, media: List[UploadFile] = File(...), access_token: str = Cookie(None)):
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

@router.post("/removeEvent/", tags=["event"])
async def removeEvent(response: Response, request: Request, eventID: int, access_token: str = Cookie(None)):
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
        
        return {"detail": f"successfully remove blog {eventID}"}
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/editEvent/", tags=["event"])
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
        
        return root.event[eventID]
    except Exception as e:
        return {"detail": str(e)}

@router.post("/addReplyEvent/", tags=["event"])
async def addReplyEvent(response: Response, request: Request, eventID: int, text: str, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        root.event[eventID].addReply(userId, text)
        root.user[root.event[eventID].author].addNotification(f"{root.user[userId].username} replied to your event, {root.event[eventID].title}", datetime.now())
        
        transaction.commit()
        
        return root.event[eventID]
    except Exception as e:
        return {"detail": str(e)}

@router.post("/addLikeReplyEvent/", tags=["event"])
async def addLikeReplyEvent(response: Response, request: Request, eventID: int, replyIndex: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        if userId in root.event[eventID].reply[replyIndex].like:
            return
            
        root.event[eventID].reply[replyIndex].addLike(userId)
        root.user[root.event[eventID].reply[replyIndex].author].addNotification(f"{root.user[userId].username} liked your reply in {root.event[eventID].title}", datetime.now())
        
        transaction.commit()
        
        return root.event[eventID]
    except Exception as e:
        return {"detail": str(e)}

@router.post("/removeLikeReplyEvent/", tags=["event"])
async def removeLikeReplyEvent(response: Response, request: Request, eventID: int, replyIndex: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        if not userId in root.event[eventID].reply[replyIndex].like:
            return
            
        root.event[eventID].reply[replyIndex].removeLike(userId)
        
        transaction.commit()
        
        return root.event[eventID]
    except Exception as e:
        return {"detail": str(e)}

@router.post("/removeReplyEvent/", tags=["event"])
async def addReplyEvent(response: Response, request: Request, eventID: int, replyIndex: str, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        if not root.event[eventID].removeReply(replyIndex, userId):
            raise Exception("user has no permission")
        
        transaction.commit()
        
        return root.event[eventID]
    except Exception as e:
        return {"detail": str(e)}

@router.post("/addAttending/", tags=["event"])
async def addAttending(response: Response, request: Request, eventID: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.event[eventID].addAttending(userId)
        root.user[root.event[eventID].author].addNotification(f"{root.user[userId].username} is attending {root.event[eventID].title}", datetime.now())
        
        transaction.commit()
        
        return root.event[eventID]
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/removeAttending/", tags=["event"])
async def removeAttending(response: Response, request: Request, eventID: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.event[eventID].removeAttending(userId)
        
        transaction.commit()
        
        return root.event[eventID]
    except Exception as e:
        return {"detail": str(e)}

@router.post("/addMaybe/", tags=["event"])
async def addMaybe(response: Response, request: Request, eventID: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.event[eventID].addMaybe(userId)
        root.user[root.event[eventID].author].addNotification(f"{root.user[userId].username} may be attending {root.event[eventID].title}", datetime.now())
        
        transaction.commit()
        
        return root.event[eventID]
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/removeMaybe/", tags=["event"])
async def removeMaybe(response: Response, request: Request, eventID: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.event[eventID].removeMaybe(userId)
        
        transaction.commit()
        
        return root.event[eventID]
    except Exception as e:
        return {"detail": str(e)}

@router.post("/addNotAttending/", tags=["event"])
async def addNotAttending(response: Response, request: Request, eventID: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.event[eventID].addNotAttending(userId)
        root.user[root.event[eventID].author].addNotification(f"{root.user[userId].username} is not attending {root.event[eventID].title}", datetime.now())
        
        transaction.commit()
        
        return root.event[eventID]
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/removeNotAttending/", tags=["event"])
async def removeNotAttending(response: Response, request: Request, eventID: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.event[eventID].removeNotAttending(userId)
        
        transaction.commit()
        
        return root.event[eventID]
    except Exception as e:
        return {"detail": str(e)}
    
@router.get("/getEvent/", tags=["event"])
async def getEvent(response: Response, request: Request, eventID: int):
    try:
        if not eventID in root.event:
            raise Exception("event not found")
        
        return root.event[eventID]
    except Exception as e:
        return {"detail": str(e)}
    
@router.get("/getCurrentEventID/", tags=["event"])
async def getCurrentEventID(response: Response, request: Request):
    return {"currentEventID": root.config["currentEventID"]}