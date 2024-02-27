
from abc import ABC, abstractmethod
from datetime import datetime

import persistent 
from persistent.list import PersistentList

class Content(persistent.Persistent, ABC):
    def __init__(self, author: str, text: str, media: list) -> None:
        self.author = author
        self.text = text
        self.media = media
        self.edited = False
        self.timestamp = datetime.now()
    
    @abstractmethod
    def editContent():
        pass

class Reply(Content):
    def __init__(self, author: str, text: str, media: list) -> None:
        super().__init__(author, text, media)
        self.like = PersistentList()

    def editContent(self, text: str, media: list):
        self.text = text
        self.media = media
        self.edited = True
        self.timestamp = datetime.now()
    
    def addLike(self, userID: str):
        self.like.append(userID)
    
    def removeLike(self, userID: str):
        self.like.pop(userID)
        
class Blog(Content):
    def __init__(self, blogID: str, title: str, author: str, text: str, media: list) -> None:
        super().__init__(author, text, media)
        self.blogID = blogID
        self.title = title
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
        
    def addReply(self, author, text, media):
        self.reply.append(Reply(author, text, media))
        
    def removeReply(self, replyIndex: str, userID: str):
        if self.reply[replyIndex].author == userID:
            self.reply.pop(replyIndex)
            return True

        return False
        
class Event(Content):
    
    def __init__(self, eventID: str, title: str, author: str, text: str, media: list, date: datetime) -> None:
        super().__init__(author, text, media)
        self.eventID = eventID
        self.title = title
        self.date = date
        self.reply = PersistentList()           # Store as obj
        self.attending = PersistentList()       # Store as ID
        self.maybe = PersistentList()           # Store as ID
        self.notAttending = PersistentList()    # Store as ID
        
    def editContent(self, title: str, text: str, media: list, date: datetime):
        self.title = title
        self.text = text
        self.media = media
        self.date = date
        self.edited = True
        self.timestamp = datetime.now()
    
    def addReply(self, author, text, media):
        self.reply.append(Reply(author, text, media))
        
    def removeReply(self, replyIndex: str, userID: str):
        if self.reply[replyIndex].author == userID:
            self.reply.pop(replyIndex)
            return True

        return False
    
    def addAttending(self, userID: str):
        self.attending.append(userID)
        
    def addMaybe(self, userID: str):
        self.attending.append(userID)
        
    def addNotAttending(self, userID: str):
        self.notAttending.append(userID)
                
    def removeAttending(self, userID: str):
        self.attending.remove(userID)
    
    def removeMaybe(self, userID: str):
        self.attending.remove(userID)
        
    def removeNotAttending(self, userID: str):
        self.notAttending.remove(userID)
    