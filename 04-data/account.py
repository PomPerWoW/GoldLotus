
from email_validator import validate_email, EmailNotValidError
from password_strength import PasswordPolicy

from hashing import hashPassword
from content import *
from database import *

class User(persistent.Persistent):
    def __init__(self, username: str, email: str, password: str) -> None:
        self.__verify_account_details(username, email, password)

        self.userID = root.user["currentID"]
        self.username = username
        self.email = email
        self.__password = hashPassword(password)
        self.post = PersistentList()
        self.event = PersistentList()
        root.user["currentID"] += 1

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

    def createPost(self, title: str, text: str, media: list):
        Post(title, self.userID, text, media)
    
    def createEvent(self, title: str, text: str, media: list,  date: datetime):
        Event(title, self.userID, text, media, date)
        