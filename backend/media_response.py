
from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
import sys
import os

router = APIRouter()

PARENT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(1, os.path.join(PARENT_DIRECTORY, "data"))

from database import *

@router.get("/media/", tags=["blog"])
async def get_media(request: Request, response: Response, mediaID: str):
    try:
        if os.path.exists(os.path.join("uploads", str(mediaID)) + ".png"):
            return str(mediaID) + ".png"
        
        elif os.path.exists(os.path.join("uploads", str(mediaID)) + ".jpg"):
            return str(mediaID) + ".jpg"
        
        elif os.path.exists(os.path.join("uploads", str(mediaID)) + ".jpeg"):
            return str(mediaID) + ".jpeg"
        
        elif os.path.exists(os.path.join("uploads", str(mediaID)) + ".MP4"):
            return str(mediaID) + ".mp4"
        
        else:
            raise Exception("File not found in the db.")

    except Exception as e:
        return {"detail": str(e)}