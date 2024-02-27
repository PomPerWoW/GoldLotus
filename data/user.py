
import persistent 
from persistent.list import PersistentList 

from email_validator import validate_email, EmailNotValidError
from password_strength import PasswordPolicy

from content import *

import hashlib
hash_algorithm = hashlib.new("SHA256")

class User(persistent.Persistent):
    def __init__(self, userID: str, username: str, email: str, password: str) -> None:
        self.__verify_account_details(username, email, password)

        self.userID = userID                            # str
        self.username = username
        self.email = email
        self.__password = self.hashPassword(password)
        self.blog = PersistentList()                    # Store as ID
        self.event = PersistentList()                   # Store as ID
        self.follower = PersistentList()                # Store as ID
        self.following = PersistentList()               # Store as ID

    def __verify_account_details(self, username: str, email: str, password: str) -> None:
        # Username
        if not 8 <= len(username) <= 16:
            raise ValueError("Username must be between 8 and 16 characters long")

        # Email
        try:
            validate_email(email)
        except EmailNotValidError:
            raise ValueError("Invalid email format")

        # Password
        policy = PasswordPolicy.from_names(
            length=8,       # Min length: 8
            uppercase=1,    # Require min. 1 uppercase letter
            nonletters=1,   # Require min. 1 non-letter character (digit, special character, etc.)
        )
        if policy.test(password):
            raise ValueError("Invalid password format")

    def hashPassword(self, password: str):  
        hash_algorithm = hashlib.new("SHA256") 
        hash_algorithm.update(password.encode())
        return hash_algorithm.hexdigest()
    
    def verifyPassword(self, password: str):
        return True if self.hashPassword(password) == self.__password else False

    def changePassword(self, password: str):
        self.__password = self.hashPassword(password)
    
    def createBlog(self, blogID: int):
        self.blog.append(blogID)
    
    def editBlog(self, blogID: int):    
        return blogID in self.blog
    
    def deleteBlog(self, targetBlog: int):
        if targetBlog in self.blog:
            self.blog.remove(targetBlog)
            return True
                
        return False
    
    def createEvent(self, eventID : int):
        self.event.append(eventID)
    
    def editEvent(self, eventID: int):
        return eventID in self.event
    
    def deleteEvent(self, targetEvent: int):
        if targetEvent in self.event:
            self.event.remove(targetEvent)
            return True
                
        return False
    
    def addFollower(self, userID: str):
        self.follower.append(userID)
    
    def addFollowing(self, userID: str):
        self.following.append(userID)
        
    def removeFollower(self, userID: str):
        self.follower.remove(userID)
    
    def removeFollowing(self, userID: str):
        self.following.remove(userID)