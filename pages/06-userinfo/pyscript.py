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
        fullUrl = window.location.href
        self.userID = fullUrl.split("/")[4]

        self.userinfoUserHeader = document.querySelector(".userinfo__user--header")
        
        # Logout
        self.userinfoLogoutBtn = document.querySelector("#userinfo__logout--btn")
        self.userinfoLogoutBtn.onclick = lambda e: self.logout(e)
        
    async def onLoad(self):
        self.myData = await self.getMyUserInfo()
        self.data = await self.getUserInfo()
        
        if self.myData.get("userID") != self.data.get("userID"):
            self.userinfoLogoutBtn.classList.add("hidden")
            
        self.loadUserInfoUser(self.data)
        
    async def getMyUserInfo(self):
        try:
            response = await pyfetch(
                url=f"/user/info", 
                method='GET', 
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                print(data)
                return data
        except Exception as e:
            print(e)
    
    async def getUserInfo(self):
        try:
            response = await pyfetch(
                url=f"/user/getUser?userId={self.userID}", 
                method='GET', 
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                print(data)
                return data
        except Exception as e:
            print(e)
    
    def logout(self, event):
        event.preventDefault()
        document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"
        window.location.href = "/"

    def loadUserInfoUser(self, userInfo):
        divLeft = document.createElement("div")
        divLeft.classList.add("div-left")
        
        userInfoUserImg = document.createElement("img")
        userInfoUserImg.classList.add("userinfo--img")
        userInfoUserImg.src = "/assets/images/monk-cartoon-1.png"
        
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
        
        userInfoUserEmail = document.createElement("div")
        userInfoUserEmail.classList.add("userinfo__user--email")

        userEmail = document.createElement("p")
        userEmail.innerHTML = f"Email: {userInfo.get('email')}"
        
        userInfoUserEmail.appendChild(userEmail)
        
        divFragment.appendChild(userInfoUserID)
        divFragment.appendChild(userInfoUserName)
        divFragment.appendChild(userInfoUserEmail)
        
        divLeft.appendChild(userInfoUserImg)
        divLeft.appendChild(divFragment)
        
        divRight = document.createElement("div")
        divRight.classList.add("div-right")
        
        userFollowingData = userInfo.get('following')
        userFollowerData = userInfo.get('follower')
        
        userFollowing = document.createElement("p")
        userFollowing.innerHTML = f"{len(userFollowingData)} Following"
        
        userFollower = document.createElement("p")
        userFollower.innerHTML = f"{len(userFollowerData)} Follower"

        divRight.appendChild(userFollowing)
        divRight.appendChild(userFollower)

        self.userinfoUserHeader.appendChild(divLeft)
        self.userinfoUserHeader.appendChild(divRight)
        
if __name__ == "__main__":
    
    w = UserInfoWidget("userinfo")
    w.initializeWidget()
    