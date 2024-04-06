
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
    
import requests    

@router.get("/gmaps/nearby")
async def gmaps_proxy(request: Request, lat: str, lon: str):
    target_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword=วัด&location={lat}%2C{lon}&radius=1500&type=tourist_attraction&key=AIzaSyDgm_2U2SClJaQ-8Hmy6UeU_dGdKb8Roh4"

    response = requests.get(target_url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"Error:", response.status_code}