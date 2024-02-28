
from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse
import sys
import os

router = APIRouter()

PARENT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(1, os.path.join(PARENT_DIRECTORY, "data"))

from database import *

@router.get("/media/")
async def get_media(request: Request, response: Response, mediaID: str):
    try:
        if os.path.exists(os.path.join("uploads", str(mediaID)) + ".png"):
            file_path = os.path.join("uploads", str(mediaID)) + ".png"
        elif os.path.exists(os.path.join("uploads", str(mediaID)) + ".jpg"):
            file_path = os.path.join("uploads", str(mediaID)) + ".jpg"
        elif os.path.exists(os.path.join("uploads", str(mediaID)) + ".jpeg"):
            file_path = os.path.join("uploads", str(mediaID)) + ".jpeg"
        elif os.path.exists(os.path.join("uploads", str(mediaID)) + ".MP4"):
            file_path = os.path.join("uploads", str(mediaID)) + ".MP4"
        else:
            raise Exception("File not found in the db.")

        return FileResponse(file_path)
    except Exception as e:
        return {"detail": str(e)}