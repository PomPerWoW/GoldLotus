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
        self.userinfoBlogBox = document.querySelector("#userinfo__blog--box")
        self.userinfoEventBox = document.querySelector("#userinfo__event--box")
        
        # Logout
        self.userinfoLogoutBtn = document.querySelector("#userinfo__logout--btn")
        self.userinfoLogoutBtn.onclick = lambda e: self.logout(e)
        
    async def onLoad(self):
        self.myData = await self.getMyUserInfo()
        self.data = await self.getUserInfo()
        
        if self.myData.get("userID") != self.data.get("userID"):
            self.userinfoLogoutBtn.classList.add("hidden")
            
        self.loadUserInfoUser(self.data)
        await self.loadUserInfoBlog(self.data.get("blog"))
        await self.loadUserInfoEvent(self.data.get("event"))
        
    async def getMyUserInfo(self):
        try:
            response = await pyfetch(
                url=f"/user/info", 
                method='GET', 
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
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
    
    async def loadBlog(self, index):
        try:
            response = await pyfetch(
                url=f"/getBlog/?blogID={index}", 
                method='GET',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                return data
        except Exception as e:
            print(e)
    
    async def loadEvent(self, index):
        try:
            response = await pyfetch(
                url=f"/getEvent/?eventID={index}", 
                method='GET',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                return data
        except Exception as e:
            print(e)
    
    async def loadUserInfoBlog(self, blogList):
        if blogList.get("data"):
            blogsData = blogList.get("data")
            for i in range(len(blogsData)):
                blogData = await self.loadBlog(blogsData[i])
                userinfoBlogPost = document.createElement("div")
                userinfoBlogPost.classList.add("userinfo__blog--post")

                userinfoBlogTitle = document.createElement("div")
                userinfoBlogTitle.classList.add("userinfo__blog--title")
                userinfoBlogTitle.innerHTML = f"{blogData.get('title')}"

                userinfoBlogText = document.createElement("div")
                userinfoBlogText.classList.add("userinfo__blog--text")
                userinfoBlogText.innerHTML = f"{blogData.get('text')}"

                userinfoBlogTimestamp = document.createElement("div")
                userinfoBlogTimestamp.classList.add("userinfo__blog--timestamp")
                
                timestampObj = datetime.fromisoformat(blogData.get('timestamp'))
                current_time = datetime.now()
                time_difference = current_time - timestampObj
                days = time_difference.days
                hours, remainder = divmod(time_difference.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                if days == 0:
                    if hours == 0:
                        if minutes == 0:
                            userinfoBlogTimestamp.innerHTML = f"{seconds} {'seconds' if seconds > 1 else 'second'} ago"
                        else:
                            userinfoBlogTimestamp.innerHTML = f"{minutes} {'minutes' if minutes > 1 else 'minute'} ago"
                    else:
                        userinfoBlogTimestamp.innerHTML = f"{hours} {'hours' if hours > 1 else 'hour'} ago"
                else:
                    userinfoBlogTimestamp.innerHTML = f"{days} {'days' if days > 1 else 'day'} ago"

                userinfoBlogPost.appendChild(userinfoBlogTitle)
                userinfoBlogPost.appendChild(userinfoBlogText)
                userinfoBlogPost.appendChild(userinfoBlogTimestamp)

                self.userinfoBlogBox.appendChild(userinfoBlogPost)
    
    async def loadUserInfoEvent(self, eventList):
        if eventList.get("data"):
            blogsData = eventList.get("data")
            for i in range(len(blogsData)):
                blogData = await self.loadEvent(blogsData[i])
                userinfoBlogPost = document.createElement("div")
                userinfoBlogPost.classList.add("userinfo__event--post")

                userinfoBlogTitle = document.createElement("div")
                userinfoBlogTitle.classList.add("userinfo__event--title")
                userinfoBlogTitle.innerHTML = f"{blogData.get('title')}"

                userinfoBlogTimestamp = document.createElement("div")
                userinfoBlogTimestamp.classList.add("userinfo__event--date")
                
                target_date_str = f"{blogData.get('date')}"
                target_date = datetime.fromisoformat(target_date_str)
                today = datetime.today()
                difference = target_date - today
                daysLeft = difference.days
                hoursLeft = difference.seconds // 3600
                minutesLeft = (difference.seconds % 3600) // 60
                secondsLeft = difference.seconds % 60
                
                formatDate = target_date.strftime("%d/%m/%Y %H:%M")
                
                if daysLeft == 0:
                    if hoursLeft == 0:
                        if minutesLeft == 0:
                            userinfoBlogTimestamp.innerHTML = f"{formatDate} ({secondsLeft} {'seconds' if secondsLeft > 1 else 'second'} left)"
                        else:
                            userinfoBlogTimestamp.innerHTML = f"{formatDate} ({minutesLeft} {'minutes' if minutesLeft > 1 else 'minute'} left)"
                    else:
                        userinfoBlogTimestamp.innerHTML = f"{formatDate} ({hoursLeft} {'hours' if hoursLeft > 1 else 'hour'} left)"
                else:
                    userinfoBlogTimestamp.innerHTML = f"{formatDate} ({daysLeft} {'days' if daysLeft > 1 else 'day'} left)"

                userinfoBlogPost.appendChild(userinfoBlogTitle)
                userinfoBlogPost.appendChild(userinfoBlogTimestamp)

                self.userinfoEventBox.appendChild(userinfoBlogPost)
    
if __name__ == "__main__":
    w = UserInfoWidget("userinfo")
    w.initializeWidget()
    