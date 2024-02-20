
from fastapi import FastAPI, Request, Response
from datetime import datetime
import sys
import os

app = FastAPI()

PARENT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(1, os.path.join(PARENT_DIRECTORY, "data"))

from user import User
from content import Post, Reply, Event
from database import *

@app.post("/postBlog/")
async def postBlog(response: Response, request: Request, username: str, email: str, password: str):
    try:
        for id in root.user:
            if username == root.user[id].username:
                raise Exception("username is already taken")
            if email == root.user[id].email:
                raise Exception("email already exist")
        
        currentUserID = root.config["currentUserID"]
        
        # userID format: "ddmmyyyyxxxxxx"   
        userID = datetime.now().strftime("%d%m%Y") + f"{currentUserID:06d}"
        root.user[userID] = User(userID, username, email, password)
        
        root.config["currentUserID"] += 1
        
        transaction.commit()
        
        return root.user[userID]
    except Exception as e:
        return {"detail": str(e)}