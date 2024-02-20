
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
from database import *
from auth.auth_handler import *

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
        
        access_token = signJWT(userID)
        response.status_code = 200
        response.set_cookie(key="access_token", value=access_token)
        
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
                    access_token = signJWT(id)
                    response.status_code = 200
                    response.set_cookie(key="access_token", value=access_token)
                    return root.user[id].__dict__
                else:
                    Exception("invalid signin information")
                            
        if not found:
            raise Exception("invalid signin information")
    except Exception as e:
        return {"detail": str(e)}

@app.get("/user/resetPassword/")
async def resetPwd(email: str):
    try:
        userID = None
        for id in root.user:
            if email == root.user[id].email:
                userID = id
            
        if userID == None:
            raise Exception("User not found") 
        
        payload = {
            "id" : userID,
            "exp" : time.time() + 600 # 10mins
        }
        token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
        
        body = f"click this link to reset your password: \nhttp://127.0.0.1:8000/user/resetPwd/{token}\n\nThis link will be valid only for 10 mins."
        email_body = MIMEText(body, "plain")
        
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = email
        message["Subject"] = RESET_PASSWORD_SUBJECT
        message.attach(email_body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, email, message.as_string())
        
        return {"detail": "Email sent successfully!"}
    except Exception as e:
        return {"detail": str(e)}