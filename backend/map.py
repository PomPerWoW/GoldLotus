
from fastapi import APIRouter, Request, Response
import sys
import os

router = APIRouter()

PARENT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(1, os.path.join(PARENT_DIRECTORY, "data"))

import requests    

@router.get("/nearbyTemple")
async def nearbyTemple(request: Request, response: Response, lat: str, lon: str):
    target_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword=วัด&location={lat}%2C{lon}&radius=1500&type=tourist_attraction&key=AIzaSyDgm_2U2SClJaQ-8Hmy6UeU_dGdKb8Roh4"

    response = requests.get(target_url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"Error:", response.status_code}