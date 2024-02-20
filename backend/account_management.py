
# Email Setup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# API 
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

@app.post("/user/signUp/")
async def signUp(response: Response, request: Request, username: str, email: str, password: str):
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

@app.get("/user/signIn/")
async def signIn(response: Response, request: Request, key: str, password: str):
    try:
        found = False
        for id in root.user:
            if key == root.user[id].username or key == root.user[id].email:
                if root.user[id].verifyPassword(password):
                    return root.user[id].__dict__
                else:
                    Exception("invalid signin information")
                            
        if not found:
            raise Exception("invalid signin information")
    except Exception as e:
        return {"detail": str(e)}
