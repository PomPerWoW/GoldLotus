
from abc import ABC, abstractmethod
from datetime import datetime

import persistent 
from persistent.list import PersistentList

class Content(persistent.Persistent, ABC):
    def __init__(self, title: str, author: str, text: str, media: list) -> None:
        self.title = title
        self.author = author
        self.text = text
        self.media = media
        self.timestamp = datetime.now()
    
    @abstractmethod
    def removeContent():
        pass
    
    @abstractmethod
    def editContent():
        pass

class Reply(Content):
    def __init__(self, title: str, author: str, text: str, media: list) -> None:
        super().__init__(title, author, text, media)
        self.like = PersistentList()

    def removeContent():
        pass
    
    def editContent():
        pass
    
    def addLike(self, userID: str):
        self.like.append(userID)
    
    def removeLike(self, userID: str):
        self.like.pop(userID)
        
class Post(Content):
    def __init__(self, postID: str, title: str, author: str, text: str, media: list) -> None:
        super().__init__(title, author, text, media)
        self.postID = postID
        self.like = PersistentList()
        self.reply = PersistentList()
        
    def removeContent(self):
        pass
    
    def editContent():
        pass
    
    def addLike(self, userID: str):
        self.like.append(userID)
        
    def removeLike(self, userID: str):
        self.like.pop(userID)
        
    def addReply(self, reply: Reply):
        self.reply.append(reply)
        
    def removeReply(self, replyIndex: str):
        self.reply.pop(replyIndex)
        
class Event(Content):
    
    def __init__(self, eventID: str, title: str, author: str, text: str, media: list, date: datetime) -> None:
        super().__init__(title, author, text, media)
        self.eventID = eventID
        self.date = date
        self.attending = PersistentList()
        self.maybe = PersistentList()
        self.notAttending = PersistentList()
        
    def removeContent():
        pass
    
    def editContent():
        pass
        
    def addAttending(self, userID: str):
        self.attending.append(userID)
        
    def addMaybe(self, userID: str):
        self.attending.append(userID)
        
    def addAttending(self, userID: str):
        self.attending.append(userID)
                
    def removeAttending(self, userID: str):
        self.attending.pop(userID)
    
    def removeMaybe(self, userID: str):
        self.attending.pop(userID)
        
    def removeAttending(self, userID: str):
        self.attending.pop(userID)
    