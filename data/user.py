
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

        self.userID = userID
        self.username = username
        self.email = email
        self.__password = self.hashPassword(password)
        self.blog = PersistentList()
        self.event = PersistentList()

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

    def hashPassword(self, password):  
        hash_algorithm = hashlib.new("SHA256") 
        hash_algorithm.update(password.encode())
        return hash_algorithm.hexdigest()
    
    def verifyPassword(self, password):
        return True if self.hashPassword(password) == self.__password else False

    def createBlog(self, blogID: str, title: str, text: str, media: list):
        newBlog = Blog(blogID, title, self.userID, text, media)
        self.blog.append(newBlog)
        
        return newBlog
     
    def deleteBlog(self, blogID: str):
        for blog in self.blog:
            if blogID == blog.blogID:
                del blog
                return True
                
        return False
    
    def createEvent(self, title: str, text: str, media: list,  date: datetime):
        Event(title, self.userID, text, media, date)
        