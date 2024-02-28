
from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
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
            return FileResponse(os.path.join("uploads", str(mediaID)) + ".png")
        
        elif os.path.exists(os.path.join("uploads", str(mediaID)) + ".jpg"):
            return FileResponse(os.path.join("uploads", str(mediaID)) + ".jpg")
        
        elif os.path.exists(os.path.join("uploads", str(mediaID)) + ".jpeg"):
            return FileResponse(os.path.join("uploads", str(mediaID)) + ".jpeg")
        
        elif os.path.exists(os.path.join("uploads", str(mediaID)) + ".MP4"):
            video_size = os.path.join("uploads", str(mediaID)) + ".MP4".stat().st_size
            def iter_file():
                with open(os.path.join("uploads", str(mediaID)) + ".MP4", "rb") as video_file:
                    while chunk := video_file.read(65536):
                        yield chunk
            return StreamingResponse(iter_file(), media_type="video/mp4", headers={"Accept-Ranges": "bytes", "Content-Length": str(video_size)})
        
        else:
            raise Exception("File not found in the db.")

    except Exception as e:
        return {"detail": str(e)}