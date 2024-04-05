
from datetime import datetime

import persistent 
from persistent.list import PersistentList

class Notification(persistent.Persistent):
    def __init__(self, text: str, timestamp: datetime):
        super().__init__()
        self.text = text
        self.timestamp = timestamp
        self.status = False
    
    def markAsRead(self):
        self.status = True