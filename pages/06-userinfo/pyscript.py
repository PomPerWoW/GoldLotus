import js
from pyscript import window, document
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch
from abc import ABC, abstractmethod
from datetime import datetime

class AbstractWidget(ABC):
    def __init__(self, element_id):
        self.element_id = element_id
        self._element = None
    
    @property
    def element(self):
        if not self._element:
            self._element = document.querySelector(f"#{self.element_id}")
        return self._element
    
    @abstractmethod
    def initializeWidget(self):
        pass
    
class UserInfoWidget(AbstractWidget):
    def __init__(self, element_id):
        super().__init__(element_id)
    
    def initializeWidget(self):
        js.Promise.resolve(self.onLoad()).catch(lambda e: print(e))

        self.userinfoUserHeader = document.querySelector(".userinfo__user--header")
        
    async def onLoad(self):
        self.data = await self.getUserInfo()
        print(self.data)
        self.loadUserInfoUser(self.data)
    
    async def getUserInfo(self):
        try:
            response = await pyfetch(
                url="/user/info", 
                method='GET', 
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                return data
        except Exception as e:
            print(e)

    def loadUserInfoUser(self, userInfo):
        divFragment = document.createElement("div")

        userInfoUserID = document.createElement("div")
        userInfoUserID.classList.add("userinfo__user--id")

        userID = document.createElement("p")
        userID.innerHTML = f"ID: {userInfo.get('userID')}"

        userInfoUserID.appendChild(userID)
        
        userInfoUserName = document.createElement("div")
        userInfoUserName.classList.add("userinfo__user--name")

        userName = document.createElement("p")
        userName.innerHTML = f"{userInfo.get('username')}"

        userInfoUserName.appendChild(userName)
        
        divFragment.appendChild(userInfoUserID)
        divFragment.appendChild(userInfoUserName)

        self.userinfoUserHeader.appendChild(divFragment)
        
if __name__ == "__main__":
    w = UserInfoWidget("userinfo")
    w.initializeWidget()
    