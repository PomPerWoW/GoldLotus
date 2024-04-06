
from abc import ABC, abstractmethod
from datetime import datetime

import persistent 
from persistent.list import PersistentList

class Content(persistent.Persistent, ABC):
    def __init__(self, author: str, text: str) -> None:
        self.author = author
        self.text = text
        self.edited = False
        self.timestamp = datetime.now()
    
    @abstractmethod
    def editContent():
        pass

class Reply(Content):
    def __init__(self, author: str, text: str) -> None:
        super().__init__(author, text)
        self.like = PersistentList()

    def editContent(self, text: str):
        self.text = text
        self.edited = True
        self.timestamp = datetime.now()
    
    def addLike(self, userID: str):
        self.like.append(userID)
    
    def removeLike(self, userID: str):
        self.like.remove(userID)
        
class Blog(Content):
    def __init__(self, blogID: int, title: str, author: str, text: str, media: list) -> None:
        super().__init__(author, text)
        self.blogID = blogID            # int
        self.title = title
        self.media = media              # Store as ID
        self.like = PersistentList()    # Store as ID
        self.reply = PersistentList()   # Store as obj
    
    def editContent(self, title: str, text: str, media: list):
        self.title = title
        self.text = text
        self.media = media
        self.edited = True
        self.timestamp = datetime.now()
    
    def addLike(self, userID: str):
        self.like.append(userID)
        
    def removeLike(self, userID: str):
        self.like.remove(userID)
        
    def addReply(self, author: str, text: str):
        self.reply.append(Reply(author, text))
        
    def removeReply(self, replyIndex: int, userID: str):
        if self.reply[replyIndex].author == userID:
            self.reply.pop(replyIndex)
            return True

        return False
        
class Event(Content):
    
    def __init__(self, eventID: int, title: str, author: str, text: str, date: datetime, location: str):
        super().__init__(author, text)
        self.eventID = eventID                  # int
        self.title = title
        self.date = date
        self.location = location
        self.reply = PersistentList()           # Store as obj
        self.attending = PersistentList()       # Store as ID
        self.maybe = PersistentList()           # Store as ID
        self.notAttending = PersistentList()    # Store as ID
        
    def editContent(self, title: str, text: str, date: datetime, location: str=None):
        self.title = title
        self.text = text
        self.location = location
        self.date = date
        self.edited = True
        self.timestamp = datetime.now()
    
    def addReply(self, author: str, text: str):
        self.reply.append(Reply(author, text))
        
    def removeReply(self, replyIndex: str, userID: str):
        if self.reply[replyIndex].author == userID:
            self.reply.pop(replyIndex)
            return True

        return False
    
    def addAttending(self, userID: str):
        self.attending.append(userID)
        if userID in self.maybe:
            self.removeMaybe(userID)
        if userID in self.notAttending:
            self.removeNotAttending(userID)
        
    def addMaybe(self, userID: str):
        self.maybe.append(userID)
        if userID in self.attending:
            self.removeAttending(userID)
        if userID in self.notAttending:
            self.removeNotAttending(userID)
        
    def addNotAttending(self, userID: str):
        self.notAttending.append(userID)
        if userID in self.maybe:
            self.removeMaybe(userID)
        if userID in self.attending:
            self.removeAttending(userID)
                
    def removeAttending(self, userID: str):
        self.attending.remove(userID)
    
    def removeMaybe(self, userID: str):
        self.maybe.remove(userID)
        
    def removeNotAttending(self, userID: str):
        self.notAttending.remove(userID)
    