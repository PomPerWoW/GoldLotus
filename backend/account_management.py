# Email Setup
from shutil import ExecError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# API 
from fastapi import APIRouter, Request, Response, Cookie
from datetime import datetime
import sys
import os

router = APIRouter()

PARENT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(1, os.path.join(PARENT_DIRECTORY, "data"))

from user import User
from email_validator import validate_email, EmailNotValidError
from password_strength import PasswordPolicy
from database import *
from auth.auth_handler import *

@router.post("/user/signUp/", tags=["User"])
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
        
        return access_token
    except Exception as e:
        return {"detail": str(e)}

@router.post("/user/signIn/", tags=["User"])
async def signIn(response: Response, request: Request, key: str, password: str):
    try:
        found = False
        for id in root.user:
            if key == root.user[id].username or key == root.user[id].email:
                if root.user[id].verifyPassword(password):
                    access_token = signJWT(id)
                    response.status_code = 200
                    response.set_cookie(key="access_token", value=access_token)
                    return access_token
                else:
                    Exception("invalid signin information")
                            
        if not found:
            raise Exception("invalid signin information")
    except Exception as e:
        return {"detail": str(e)}

@router.post("/user/resetPassword/", tags=["User"])
async def resetPassword(response: Response, request: Request, email: str):
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
        
        body = f"click this link to reset your password: \nhttp://127.0.0.1:8000/setpassword/{token}\n\nThis link will be valid only for 10 mins."
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

@router.post("/user/setNewPassword/", tags=["User"])
async def setNewPassword(response: Response, request: Request, token: str, password: str):
    try:
        policy = PasswordPolicy.from_names(
            length=8,       # Min length: 8
            uppercase=1,    # Require min. 1 uppercase letter
            nonletters=1,   # Require min. 1 non-letter character (digit, special character, etc.)
        )
        if policy.test(password):
            raise Exception("Invalid password format")
        
        userID = decodeJWT(token)["id"]
        root.user[userID].changePassword(password)
        
        transaction.commit()
        
        return {"detail": "successful"}
    except Exception as e:
        return {"detail": str(e)}

@router.post("/user/changeEmail/", tags=["User"])
async def changeEmail(response: Response, request: Request, email: str, access_token: str = Cookie(None)):
    try:
        try:
            validate_email(email)
        except EmailNotValidError:
            raise Exception("Invalid email format")
        
        for id in root.user:
            if email == root.user[id].email:
                raise Exception("email already exist")
        
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        root.user[userId].changeEmail(email)
        
        transaction.commit()
        
        return root.user[userId]
    except Exception as e:
        return {"detail": str(e)}

@router.post("/user/changeUsername/", tags=["User"])
async def changeUsername(response: Response, request: Request, username: str, access_token: str = Cookie(None)):
    try:
        if not 8 <= len(username) <= 16:
            raise Exception("Username must be between 8 and 16 characters long")
        
        for id in root.user:
            if username == root.user[id].username:
                raise Exception("username is already taken")
        
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        root.user[userId].changeUsername(username)
        
        transaction.commit()
        
        return root.user[userId]
    except Exception as e:
        return {"detail": str(e)}

@router.get("/user/info", tags=["User"])
async def getUserInfo(response: Response, request: Request, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        user = root.user[userId]
        
        return {"userID": user.userID, "username": user.username, "email": user.email, "blog": user.blog, "event": user.event, "follower": user.follower, "following": user.following}
    except Exception as e:
        return {"detail": str(e)}

@router.get("/user/getUser", tags=["User"])
async def getUser(response: Response, request: Request, userId: str):
    try:
        user = root.user[userId]
        
        return {"userID": user.userID, "username": user.username, "email": user.email, "blog": user.blog, "event": user.event, "follower": user.follower, "following": user.following}
    except Exception as e:
        return {"detail": str(e)}

@router.post("/user/follow", tags=["User"])
async def follow(response: Response, request: Request, followingID: str, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.user[userId].addFollowing(followingID)
        
        root.user[followingID].addFollower(userId)
        root.user[followingID].addNotification(f"{root.user[userId].username} has started following you.", datetime.now())
        
        transaction.commit()
        
        return root.user[userId]
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/user/unfollow", tags=["User"])
async def unfollow(response: Response, request: Request, followingID: str, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        if not userId in root.user:
            raise Exception("author not found")
        
        root.user[userId].removeFollowing(followingID)
        root.user[followingID].removeFollower(userId)
        
        transaction.commit()
        
        return root.user[userId]
    except Exception as e:
        return {"detail": str(e)}
    
@router.get("/user/getSortedIdByFollower", tags=["User"])
async def getSortedIdByFollower(response: Response, request: Request):
    try:
        result = []
        for u in sorted(root.user.values(), key=lambda user: len(user.follower), reverse=True):
            result.append(u.userID)
        
        return result
    except Exception as e:
        return {"detail": str(e)}

@router.get("/user/getAllNotification", tags=["User"])
async def getAllNotification(response: Response, request: Request, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
    
        return root.user[userId].notification
    except Exception as e:
        return {"detail": str(e)}

@router.post("/user/markAllNotificationsAsRead", tags=["User"])
async def markAllNotificationsAsRead(response: Response, request: Request, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        root.user[userId].markAllAsRead()
        
        transaction.commit()
        
        return {"detail": "all notifications are marked as read"}
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/user/removeNotification", tags=["User"])
async def removeNotification(response: Response, request: Request, index: int, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        root.user[userId].removeNotification(index)
        
        transaction.commit()
        
        return root.user[userId]
    except Exception as e:
        return {"detail": str(e)}
    
@router.post("/user/removeAllNotification", tags=["User"])
async def removeAllNotification(response: Response, request: Request, access_token: str = Cookie(None)):
    try:
        token = decodeJWT(access_token)
        userId = token["userId"]
        
        root.user[userId].removeAllNotification()
        
        transaction.commit()
        
        return root.user[userId]
    except Exception as e:
        return {"detail": str(e)}
