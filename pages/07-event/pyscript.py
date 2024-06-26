import asyncio
import js
from pyscript import window, document
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch
from abc import ABC, abstractmethod
from datetime import datetime
import time

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
    
class BlogWidget(AbstractWidget):
    def __init__(self, element_id):
        super().__init__(element_id)
    
    def initializeWidget(self):
        self.allFiles = []
        self.counter = 0
        self.body = document.querySelector("body")
        self.createPostAssets = document.querySelector(".blog__create-post--assets")
        self.listSection = document.querySelector(".blog__create-post--assets-list")
        self.assetsList = document.querySelector(".assets-list")
        self.blogCreateBtn = document.querySelector("#submit__btn")
        self.resetBtn = document.querySelector("#reset__btn")
        self.successBox = document.querySelector("#success__box")
        self.errorBox = document.querySelector("#error__box")
        self.statusBox1 = document.querySelector("#error__box--btn")
        
        self.blogCreateBtn.onclick = self.uploadFile
        self.resetBtn.onclick = self.resetInput
        self.statusBox1.onclick = lambda e: self.removeStatus(e)
    
    def createLoad(self):
        elementLoaderBox = document.createElement("div")
        elementLoaderBox.classList.add("element__page-loader--box")

        elementLoader = document.createElement("div")
        elementLoader.classList.add("element__page-loader")
        
        elementLoaderBox.appendChild(elementLoader)
        
        self.body.appendChild(elementLoaderBox)
        
    async def getLocation(self):
        location = document.querySelector("#location").value
        if location != "":
            self.createLoad()
            await self.get_place_id(location)
            await asyncio.sleep(1)
            elements = document.querySelectorAll('.element__page-loader--box')
        
            for elem in elements:
                elem.parentNode.removeChild(elem)
                
            placeID = document.querySelector("#placeID").innerHTML   
            print(placeID)
            return placeID
        return ""
    
    async def uploadFile(self, event):
        event.preventDefault()
        title = document.querySelector("#title").value
        text = document.querySelector("#text").value
        date = document.querySelector("#date").value
        placeID = await self.getLocation()
        
        if title == "" or text == "" or date == "":
            self.errorBox.classList.remove("hidden")
        else:
            date_time_obj = datetime.fromisoformat(date)
            current_datetime = datetime.now()

            if date_time_obj > current_datetime:
                if placeID == "":
                    print("yes")
                    try:
                        response = await pyfetch(
                            url=f"/createEvent/?title={title}&text={text}&date={date}",
                            method='POST',
                            headers={'Content-Type': 'application/json'}
                        )

                        if response.ok:
                            data = await response.json()
                            self.successBox.classList.remove("hidden")
                            self.resetInput(event)
                            return data
                    except Exception as error:
                        print('Error:', error)
                else:
                    try:
                        response = await pyfetch(
                            url=f"/createEvent/?title={title}&text={text}&date={date}&location={placeID}",
                            method='POST',
                            headers={'Content-Type': 'application/json'}
                        )

                        if response.ok:
                            data = await response.json()
                            self.successBox.classList.remove("hidden")
                            self.resetInput(event)
                            return data
                    except Exception as error:
                        print('Error:', error)
            else:
                self.errorBox.classList.remove("hidden")

    async def get_place_id(self, place_name):
        javascript_code = f"""
            async function getPlaceID() {{
                var request = {{
                    query: '{place_name}',
                    fields: ['place_id']
                }};

                var service = new google.maps.places.PlacesService(document.createElement('div'));

                service.textSearch(request, function (results, status) {{
                    if (status === google.maps.places.PlacesServiceStatus.OK) {{
                        if (results && results.length > 0) {{
                            var placeID = results[0].place_id;
                            document.getElementById('placeID').innerText = placeID;
                        }} else {{
                            document.getElementById('placeID').innerText = "No results found";
                        }}
                    }} else {{
                        document.getElementById('placeID').innerText = "Error: " + status;
                    }}
                }});
            }}
            
            getPlaceID()
        """
        
        js.eval(javascript_code)
            
    def resetInput(self, event):
        event.preventDefault()
        document.querySelector("#title").value = ""
        document.querySelector("#date").value = ""
        document.querySelector("#text").value = ""
        document.querySelector("#location").value = ""
    
    def removeStatus(self, event):
        event.preventDefault()
        self.errorBox.classList.add("hidden")
        self.resetInput(event)

class LoadBlogWidget(AbstractWidget):
    def __init__(self, element_id):
        super().__init__(element_id)
    
    def initializeWidget(self):
        js.Promise.resolve(self.onLoad()).catch(lambda e: print(e))
        self.blogPostBox = document.querySelector("#blog__post--box")
        self.blogPost = document.querySelector("#blog__post--create")
        self.blogPostGuest = document.querySelector("#blog__post--guest")
        self.successBox = document.querySelector("#success__box")
        self.successBoxBtn = document.querySelector("#success__box--btn")
        self.currentLatestBlogIDSaved = 0
        self.currentMyEventBlogIDSaved = 0
        
        self.successBoxBtn.onclick = self.createNewPostSuccess
        
        # Pagination
        self.blogPagLatest = document.querySelector(".blog__pagination--latest")
        self.blogPagPopular = document.querySelector(".blog__pagination--popular")
        self.blogPagFollowing = document.querySelector(".blog__pagination--following")
        self.blogPagMypost = document.querySelector(".blog__pagination--mypost")
        # Btn
        self.blogPagLatest = document.querySelector("#blog__pagination--latest")
        self.blogPagMyEvent = document.querySelector("#blog__pagination--myevent")
        
        self.blogPagLatest.onclick = self.loadAllEvent
        self.blogPagMyEvent.onclick = self.loadMyEvent

        self.likedBox = document.querySelector("#liked__box")
        self.unLikedBox = document.querySelector("#unliked__box")
        self.attendingBox = document.querySelector("#attending__box")
        self.notAttendingBox = document.querySelector("#notattending__box")
        self.maybeBox = document.querySelector("#maybe__box")
        self.commentedBox = document.querySelector("#commented__box")
        self.followedBox = document.querySelector("#followed__box")
        self.unFollowedBox = document.querySelector("#unfollowed__box")

        # Blog comment
        self.userComments = document.querySelector("#user__comments")
        self.addComments = document.querySelector("#add__comment")
        self.cancelComments = document.querySelector("#cancel__comment")
        self.userCommentCreate = document.querySelector("#user__comments--create")
        self.userComponentBody = document.querySelector("#user__component--body")
        self.userCommentOkBtn = document.querySelector("#user__comments--btn")
        self.userCommentTextInput = document.querySelector("#user__comments--text-input")
        self.userCommentsPublishBtn = document.querySelector("#user__comments--publish-btn")
        
        self.addComments.onclick = lambda _: self.showAddComments()
        self.cancelComments.onclick = lambda _: self.showCancelComments()
        self.userCommentOkBtn.onclick = lambda _: self.showOk()
        
        # Communities
        self.blogCommunities = document.querySelector("#blog__communities")
        
    async def onLoad(self):
        self.data = await self.getUserInfo()
        if self.data.get("detail") == "'NoneType' object is not subscriptable":
            self.guestUser()
        
        await self.loadAllEvent()
        
        self.membersList = await self.getListMembers()
        
        for i in range(len(self.membersList)):
            if self.membersList[i] != self.data.get("userID"):
                await self.loadMembers(self.membersList[i])
    
    async def createNewPostSuccess(self, event):
        event.preventDefault()
        self.successBox.classList.add("hidden")
        
        await self.loadAllEvent()
    
    def removeBlogPosts(self):
        blogPosts = document.querySelectorAll(".blog__post--element")
        for post in blogPosts:
            post.parentNode.removeChild(post)
    
    async def loadAllEvent(self, event=None, viewMore=False, notView=True):
        if event:
            event.preventDefault()
        
        if not viewMore:
            self.removeBlogPosts()
        
        if notView:
            self.currentLatestBlogIDSaved = 0

        viewMoreElement = document.querySelector("#blog__readmore-btn")
        if viewMoreElement:
            viewMoreElement.parentNode.removeChild(viewMoreElement)

        self.blogLists = await self.trackBlog()
        counter = 0
        currentBlogID = self.currentLatestBlogIDSaved if self.currentLatestBlogIDSaved != 0 else self.blogLists.get("currentEventID") - 1
        
        while counter < 10 and currentBlogID != 0:
            blogData = await self.loadBlog(currentBlogID)
            
            if not blogData.get("detail"):
                target_date_str = f"{blogData.get('date')}"
                target_date = datetime.fromisoformat(target_date_str)
                today = datetime.today()

                if target_date > today:
                    await self.createBlog(blogData)
                    counter += 1
                    currentBlogID -= 1
                else:
                    await self.removeEvent(blogData.get("eventID"))
                    currentBlogID -= 1
            else:
                currentBlogID -= 1
                

        self.currentLatestBlogIDSaved = currentBlogID
        
        if currentBlogID != 0 and self.currentLatestBlogIDSaved != 0:
            self.createViewMore("loadAllEvent")
    
    async def removeEvent(self, blogID):
        try:
            response = await pyfetch(
                url=f"/removeEvent/?eventID={blogID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                return data
        except Exception as e:
            print(e)
    
    async def loadMyEvent(self, event, viewMore=False, notView=True):
        if event:
            event.preventDefault()
            
        if viewMore == False:
            self.removeBlogPosts()
        
        if notView:
            self.currentMyEventBlogIDSaved = 0
        
        viewMoreElement = document.querySelector("#blog__readmore-btn")
        if viewMoreElement:
            viewMoreElement.parentNode.removeChild(viewMoreElement)
            
        userData = await self.getUserInfo()
        self.blogLists = userData.get("event")
        if self.blogLists.get("data"):
            blogListsData = self.blogLists.get("data")
            counter = 0
            currentBlogID = self.currentMyEventBlogIDSaved if self.currentMyEventBlogIDSaved != 0 else len(blogListsData)

            while counter < 10 and currentBlogID != 0:
                blogData = await self.loadBlog(blogListsData[currentBlogID - 1])
                if blogData.get("detail") != "blog not found":
                    await self.createBlog(blogData)
                    counter += 1
                currentBlogID -= 1

            self.currentMyEventBlogIDSaved = currentBlogID
            
            if currentBlogID != 0 and self.currentMyEventBlogIDSaved != 0:
                self.createViewMore("loadMyEvent")
    
    async def loadAttending(self, event, viewMore=False, notView=True):
        pass
                    
    async def loadMaybe(self, event, viewMore=False, notView=True):
        pass

    async def loadNotAttending(self, event, viewMore=False, notView=True):
        pass

    def createViewMore(self, blogType):
        viewMore = document.createElement("div")
        viewMore.id = "blog__readmore-btn"
        viewMore.classList.add("blog__readmore-btn")
        
        viewMoreBtn = document.createElement("p")
        viewMoreBtn.innerHTML = "View More"
        if blogType == "loadAllEvent":
            viewMoreBtn.onclick = lambda event: asyncio.ensure_future(self.loadAllEvent(event, True, False))
        elif blogType == "loadMyEvent":
            viewMoreBtn.onclick = lambda event: asyncio.ensure_future(self.loadMyEvent(event, True, False))
        elif blogType == "loadAttending":
            viewMoreBtn.onclick = lambda event: asyncio.ensure_future(self.loadAttending(event, True, False))
        elif blogType == "loadMaybe":
            viewMoreBtn.onclick = lambda event: asyncio.ensure_future(self.loadMaybe(event, True, False))
        elif blogType == "loadNotAttending":
            viewMoreBtn.onclick = lambda event: asyncio.ensure_future(self.loadNotAttending(event, True, False))
        
        viewMore.appendChild(viewMoreBtn)
        
        self.blogPostBox.appendChild(viewMore)

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
            
    async def loadBlog(self, index):
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
    
    async def trackBlog(self):
        try:
            response = await pyfetch(
                url=f"/getCurrentEventID/", 
                method='GET',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                return data
        except Exception as e:
            print(e)
    
    def guestUser(self):
        self.blogPostGuest.classList.remove("hidden")
        self.blogPost.style.display = "none"
        self.blogPagFollowing.style.display = "none"
        self.blogPagMypost.style.display = "none"

    def createLoad(self):
        elementLoaderBox = document.createElement("div")
        elementLoaderBox.classList.add("element__loader--box")

        elementLoader = document.createElement("div")
        elementLoader.classList.add("element__loader")
        
        elementLoaderBox.appendChild(elementLoader)
        
        self.blogPostBox.appendChild(elementLoaderBox)
    
    async def getUserDetail(self, userID):
        try:
            response = await pyfetch(
                url=f"/user/getUser?userId={userID}", 
                method='GET',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                return data
        except Exception as e:
            print(e) 
    
    async def attendingBtnAdd(self, event, blogID, btnLiked):
        event.preventDefault()
        try:
            response = await pyfetch(
                url=f"/addAttending/?eventID={blogID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()

                blogLikesCount = document.querySelector(f"#blog-attending-count-{blogID}")
                counter = blogLikesCount.innerHTML.split()[1]
                counterNew = int(counter) + 1
                
                blogLikesCount.innerHTML = f"attending {counterNew}"
                
                btnLiked.onclick = lambda event: asyncio.ensure_future(self.attendingBtnRemove(event, blogID, btnLiked))
                self.clearPreviousClicked(blogID)
                btnLiked.classList.add(f"clicked")
                self.attendingBox.classList.remove("hidden")
                await asyncio.sleep(2)
                self.attendingBox.classList.add("hidden")
                return data
        except Exception as e:
            print(e)
        
    async def attendingBtnRemove(self, event, blogID, btnLiked):
        event.preventDefault()
        try:
            response = await pyfetch(
                url=f"/removeAttending/?eventID={blogID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()

                blogLikesCount = document.querySelector(f"#blog-attending-count-{blogID}")
                counter = blogLikesCount.innerHTML.split()[1]
                counterNew = int(counter) - 1
                
                blogLikesCount.innerHTML = f"attending {counterNew}"

                btnLiked.classList.remove(f"clicked")
                btnLiked.onclick = lambda event: asyncio.ensure_future(self.attendingBtnAdd(event, blogID, btnLiked))
                return data
        except Exception as e:
            print(e)
    
    async def maybeBtnAdd(self, event, blogID, btnLiked):
        event.preventDefault()
        try:
            response = await pyfetch(
                url=f"/addMaybe/?eventID={blogID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()

                blogLikesCount = document.querySelector(f"#blog-maybe-count-{blogID}")
                counter = blogLikesCount.innerHTML.split()[1]
                counterNew = int(counter) + 1
                
                blogLikesCount.innerHTML = f"maybe {counterNew}"
                
                btnLiked.onclick = lambda event: asyncio.ensure_future(self.maybeBtnRemove(event, blogID, btnLiked))
                self.clearPreviousClicked(blogID)
                btnLiked.classList.add(f"clicked")
                self.maybeBox.classList.remove("hidden")
                await asyncio.sleep(2)
                self.maybeBox.classList.add("hidden")
                return data
        except Exception as e:
            print(e)
        
    async def maybeBtnRemove(self, event, blogID, btnLiked):
        event.preventDefault()
        try:
            response = await pyfetch(
                url=f"/removeMaybe/?eventID={blogID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()

                blogLikesCount = document.querySelector(f"#blog-maybe-count-{blogID}")
                counter = blogLikesCount.innerHTML.split()[1]
                counterNew = int(counter) - 1
                
                blogLikesCount.innerHTML = f"maybe {counterNew}"

                btnLiked.classList.remove(f"clicked")
                btnLiked.onclick = lambda event: asyncio.ensure_future(self.maybeBtnAdd(event, blogID, btnLiked))
                return data
        except Exception as e:
            print(e)
    
    async def notAttendingBtnAdd(self, event, blogID, btnLiked):
        event.preventDefault()
        try:
            response = await pyfetch(
                url=f"/addNotAttending/?eventID={blogID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()

                blogLikesCount = document.querySelector(f"#blog-notattending-count-{blogID}")
                counter = blogLikesCount.innerHTML.split()[1]
                counterNew = int(counter) + 1
                
                blogLikesCount.innerHTML = f"notattending {counterNew}"
                
                btnLiked.onclick = lambda event: asyncio.ensure_future(self.notAttendingBtnRemove(event, blogID, btnLiked))
                self.clearPreviousClicked(blogID)
                btnLiked.classList.add(f"clicked")
                self.notAttendingBox.classList.remove("hidden")
                await asyncio.sleep(2)
                self.notAttendingBox.classList.add("hidden")
                return data
        except Exception as e:
            print(e)
        
    async def notAttendingBtnRemove(self, event, blogID, btnLiked):
        event.preventDefault()
        try:
            response = await pyfetch(
                url=f"/removeNotAttending/?eventID={blogID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()

                blogLikesCount = document.querySelector(f"#blog-notattending-count-{blogID}")
                counter = blogLikesCount.innerHTML.split()[1]
                counterNew = int(counter) - 1
                
                blogLikesCount.innerHTML = f"notattending {counterNew}"

                btnLiked.classList.remove(f"clicked")
                btnLiked.onclick = lambda event: asyncio.ensure_future(self.notAttendingBtnAdd(event, blogID, btnLiked))
                return data
        except Exception as e:
            print(e)
    
    async def listAttendingUser(self, event, blogID):
        event.preventDefault()
        currentBlog = await self.loadBlog(blogID)
        print(currentBlog.get("attending"))
        
    async def listMaybeUser(self, event, blogID):
        event.preventDefault()
        currentBlog = await self.loadBlog(blogID)
        print(currentBlog.get("maybe"))
        
    def clearPreviousClicked(self, blogID):
        currentBlog = document.querySelector(f"#blog-{blogID}")
        previousElemClicked = currentBlog.querySelector(f".clicked")
        if previousElemClicked:
            previousElemClicked.classList.remove(f"clicked")
            parentElem = previousElemClicked.id.split("-")
            countElem = document.querySelector(f"#blog-{parentElem[1]}-count-{parentElem[3]}")
            countNum = countElem.innerHTML.split()[1]
            countNum = int(countNum) - 1
            if parentElem[1] == "attending":
                previousElemClicked.onclick = lambda event: asyncio.ensure_future(self.attendingBtnAdd(event, blogID, previousElemClicked))
            elif parentElem[1] == "maybe":
                previousElemClicked.onclick = lambda event: asyncio.ensure_future(self.maybeBtnAdd(event, blogID, previousElemClicked))
            elif parentElem[1] == "notattending":
                previousElemClicked.onclick = lambda event: asyncio.ensure_future(self.notAttendingBtnAdd(event, blogID, previousElemClicked))
            countElem.innerHTML = f"{parentElem[1]} {countNum}"
        
    async def listNotAttendingUser(self, event, blogID):
        event.preventDefault()
        currentBlog = await self.loadBlog(blogID)
        print(currentBlog.get("notattending"))
    
    def showAddComments(self):
        self.userCommentCreate.classList.remove("hidden")
        self.addComments.classList.add("hidden")
        self.cancelComments.classList.remove("hidden")
        
    def showCancelComments(self):
        self.userCommentCreate.classList.add("hidden")
        self.addComments.classList.remove("hidden")
        self.cancelComments.classList.add("hidden")
    
    def showOk(self):
        self.userComments.classList.add("hidden")
        self.showCancelComments()
    
    async def listCommentUser(self, event, blogDataComment, blogID):
        event.preventDefault()
        self.userComments.classList.remove("hidden")
        blogComments = document.querySelectorAll(".user__comments--person")
        for post in blogComments:
            post.parentNode.removeChild(post)
        dataComment = blogDataComment.get("data")
        self.userCommentsPublishBtn.onclick = lambda event: asyncio.ensure_future(self.publishComment(event, blogID))
        for index, data in enumerate(dataComment):
            userDetail = await self.getUserDetail(data.get("author"))
            self.createComments(blogID, data, index, userDetail)
    
    def listNoComment(self, blogID):
        self.userComments.classList.remove("hidden")
        blogComments = document.querySelectorAll(".user__comments--person")
        for post in blogComments:
            post.parentNode.removeChild(post)
        
        self.userCommentsPublishBtn.onclick = lambda event: asyncio.ensure_future(self.publishComment(event, blogID))
        
        userCommentsNoComment = document.createElement("div")
        userCommentsNoComment.classList.add("user__comments--person")

        userCommentsUpper = document.createElement("div")
        userCommentsUpper.classList.add("user__comments--upper")

        userCommentsName = document.createElement("div")
        userCommentsName.classList.add("user__comments--name")
        userCommentsName.innerHTML = "No Comments."

        userCommentsUpper.appendChild(userCommentsName)
        userCommentsNoComment.appendChild(userCommentsUpper)
        self.userComponentBody.appendChild(userCommentsNoComment)
    
    async def publishComment(self, event, blogID):
        event.preventDefault()
        commentText = self.userCommentTextInput.value
        try:
            response = await pyfetch(
                url=f"/addReplyEvent/?eventID={blogID}&text={commentText}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                self.showCancelComments()
                self.userCommentTextInput.value = ""
                blogCommentsCount = document.querySelector(f"#blog__comments--count-{blogID}")
                counter = blogCommentsCount.innerHTML.split()[0]
                counterNew = int(counter) + 1
                
                blogCommentsCount.innerHTML = f"{counterNew} comments"
                
                blogData = await self.loadBlog(blogID)
                blogDataComment = blogData.get("reply")
                
                await self.listCommentUser(event, blogDataComment, blogID)
                
                self.commentedBox.classList.remove("hidden")
                await asyncio.sleep(2)
                self.commentedBox.classList.add("hidden")
                
                return data
        except Exception as e:
            print(e)
    
    async def replyLikeBtnAdd(self, event, blogID, commentID, btnLiked):
        event.preventDefault()
        try:
            response = await pyfetch(
                url=f"/addLikeReplyEvent/?eventID={blogID}&replyIndex={commentID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()

                commentLikeCount = document.querySelector(f"#comment__likes--count-{commentID}")
                counter = commentLikeCount.innerHTML.split()[0]
                counterNew = int(counter) + 1
                
                commentLikeCount.innerHTML = f"{counterNew} likes"
                
                btnLiked.classList.add(f"clicked")
                btnLiked.onclick = lambda event: asyncio.ensure_future(self.replyLikeBtnRemove(event, blogID, commentID, btnLiked))
                self.likedBox.classList.remove("hidden")
                await asyncio.sleep(2)
                self.likedBox.classList.add("hidden")
                return data
        except Exception as e:
            print(e)
    
    async def replyLikeBtnRemove(self, event, blogID, commentID, btnLiked):
        event.preventDefault()
        try:
            response = await pyfetch(
                url=f"/removeLikeReplyEvent/?eventID={blogID}&replyIndex={commentID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                commentLikeCount = document.querySelector(f"#comment__likes--count-{commentID}")
                counter = commentLikeCount.innerHTML.split()[0]
                counterNew = int(counter) - 1
                
                commentLikeCount.innerHTML = f"{counterNew} likes"

                btnLiked.classList.remove(f"clicked")
                btnLiked.onclick = lambda event: asyncio.ensure_future(self.replyLikeBtnAdd(event, blogID, commentID,btnLiked))
                self.unLikedBox.classList.remove("hidden")
                await asyncio.sleep(2)
                self.unLikedBox.classList.add("hidden")
                return data
        except Exception as e:
            print(e)
    
    def createComments(self, blogID, commentData, commentID, userDetail):
        userCommentsPerson = document.createElement("div")
        userCommentsPerson.classList.add("user__comments--person")
        userCommentsPerson.id = f"user__comments--person-{commentID}"
        
        userCommentsUpper = document.createElement("div")
        userCommentsUpper.classList.add("user__comments--upper")
        
        userCommentsName = document.createElement("a")
        userCommentsName.classList.add("user__comments--name")
        userCommentsName.innerHTML = f"{userDetail.get('username')}"
        userCommentsName.href = f"/userInfo/{userDetail.get('userID')}"

        userCommentsTimestamp = document.createElement("div")
        userCommentsTimestamp.classList.add("user__comments--timestamp")
        
        timestampObj = datetime.fromisoformat(commentData.get('timestamp'))
        current_time = datetime.now()
        time_difference = current_time - timestampObj
        days = time_difference.days
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days == 0:
            if hours == 0:
                if minutes == 0:
                    userCommentsTimestamp.innerHTML = f"{seconds} {'seconds' if seconds > 1 else 'second'} ago"
                else:
                    userCommentsTimestamp.innerHTML = f"{minutes} {'minutes' if minutes > 1 else 'minute'} ago"
            else:
                userCommentsTimestamp.innerHTML = f"{hours} {'hours' if hours > 1 else 'hour'} ago"
        else:
            userCommentsTimestamp.innerHTML = f"{days} {'days' if days > 1 else 'day'} ago"
        
        userCommentsUpper.appendChild(userCommentsName)
        userCommentsUpper.appendChild(userCommentsTimestamp)

        userCommentsText = document.createElement("div")
        userCommentsText.classList.add("user__comments--text")
        
        text = document.createElement("p")
        text.innerHTML = f"{commentData.get('text')}"

        userCommentsText.appendChild(text)

        commentLikeData = commentData.get("like")

        userCommentsLike = document.createElement("div")
        userCommentsLike.classList.add("user__comments--like")

        iconLiked = document.createElement("i")
        iconLiked.classList.add("fa-solid", "fa-heart")

        likeSpan = document.createElement("span")
        likeSpan.id = f"comment__likes--count-{commentID}"
        
        if not self.data.get("detail"):
            if commentLikeData.get("data"):
                likeList = commentLikeData.get("data")
                likeSpan.innerHTML = f"{len(likeList)} likes"
                if self.data.get("userID") in commentLikeData.get("data"):
                    iconLiked.classList.add(f"clicked")
                    iconLiked.onclick = lambda event: asyncio.ensure_future(self.replyLikeBtnRemove(event, blogID, commentID, iconLiked))
                else:
                    iconLiked.onclick = lambda event: asyncio.ensure_future(self.replyLikeBtnAdd(event, blogID, commentID, iconLiked))
            else:      
                iconLiked.onclick = lambda event: asyncio.ensure_future(self.replyLikeBtnAdd(event, blogID, commentID, iconLiked))
                likeSpan.innerHTML = "0 likes"

        userCommentsLike.appendChild(iconLiked)
        userCommentsLike.appendChild(likeSpan)

        userCommentsPerson.appendChild(userCommentsUpper)
        userCommentsPerson.appendChild(userCommentsText)
        userCommentsPerson.appendChild(userCommentsLike)
        
        self.userComponentBody.appendChild(userCommentsPerson)
            
    async def createBlog(self, blogData):
        self.createLoad()
        
        blogID = blogData.get("eventID")
        
        userDetail = await self.getUserDetail(blogData.get("author"))
        authorName = userDetail.get("username")
        
        blogPost = document.createElement("div")
        blogPost.classList.add("blog__post", "blog__post--element")
        blogPost.id = f"blog-{blogID}"

        blogPostHeader = document.createElement("div")
        blogPostHeader.classList.add("blog__post--header")
        
        blogPostUsername = document.createElement("a")
        blogPostUsername.classList.add("blog__post--username")    
        blogPostUsername.innerHTML = f"{authorName}"
        blogPostUsername.href = f"/userInfo/{blogData.get('author')}"

        blogPostPosted = document.createElement("div")
        blogPostPosted.classList.add("blog__post--posted")
        blogPostPosted.innerHTML = f"Posted by {authorName}"

        blogPostTimestamp = document.createElement("div")
        blogPostTimestamp.classList.add("blog__post--timestamp")
        
        timestampObj = datetime.fromisoformat(blogData.get('timestamp'))
        current_time = datetime.now()
        time_difference = current_time - timestampObj
        days = time_difference.days
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days == 0:
            if hours == 0:
                if minutes == 0:
                    blogPostTimestamp.innerHTML = f"{seconds} {'seconds' if seconds > 1 else 'second'} ago"
                else:
                    blogPostTimestamp.innerHTML = f"{minutes} {'minutes' if minutes > 1 else 'minute'} ago"
            else:
                blogPostTimestamp.innerHTML = f"{hours} {'hours' if hours > 1 else 'hour'} ago"
        else:
            blogPostTimestamp.innerHTML = f"{days} {'days' if days > 1 else 'day'} ago"

        blogPostHeader.appendChild(blogPostUsername)
        blogPostHeader.appendChild(blogPostPosted)
        blogPostHeader.appendChild(blogPostTimestamp)

        blogPostField = document.createElement("div")
        blogPostField.classList.add("blog__post--field")

        blogPostTitle = document.createElement("div")
        blogPostTitle.classList.add("blog__post--title")

        blogPostTitleH3 = document.createElement("h3")
        
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
                    blogPostTitleH3.innerHTML = f"{blogData.get('title')}, {formatDate} ({secondsLeft} {'seconds' if secondsLeft > 1 else 'second'} left)"
                else:
                    blogPostTitleH3.innerHTML = f"{blogData.get('title')}, {formatDate} ({minutesLeft} {'minutes' if minutesLeft > 1 else 'minute'} left)"
            else:
                blogPostTitleH3.innerHTML = f"{blogData.get('title')}, {formatDate} ({hoursLeft} {'hours' if hoursLeft > 1 else 'hour'} left)"
        else:
            blogPostTitleH3.innerHTML = f"{blogData.get('title')}, {formatDate} ({daysLeft} {'days' if daysLeft > 1 else 'day'} left)"

        blogPostTitle.appendChild(blogPostTitleH3)

        blogPostMessage = document.createElement("div")
        blogPostMessage.classList.add("blog__post--message")

        blogPostMessageP = document.createElement("p")
        blogPostMessageP.innerHTML = f"{blogData.get('text')}"

        blogPostMessage.appendChild(blogPostMessageP)
        
        placeID = blogData.get("location")
        
        blogPostField.appendChild(blogPostTitle)
        blogPostField.appendChild(blogPostMessage)
        
        if placeID != None:
            blogPostLocation = document.createElement("iframe")
            blogPostLocation.classList.add("map")
            blogPostLocation.src = f"https://www.google.com/maps/embed/v1/place?q=place_id:{placeID}&key=AIzaSyDgm_2U2SClJaQ-8Hmy6UeU_dGdKb8Roh4"
            blogPostField.appendChild(blogPostLocation)

        blogPostFooter = document.createElement("div")
        blogPostFooter.classList.add("blog__post--footer")
        
        # Attending
        blogDataAttending = blogData.get("attending")

        blogPostAttending = document.createElement("div")
        blogPostAttending.classList.add("blog__post--like", "blog__post--footer-btn")
        
        iconAttending = document.createElement("i")
        iconAttending.id = f"blog-attending-icon-{blogID}"
        
        if not self.data.get("detail"):
            iconAttending.classList.add("fa-solid", "fa-eye")
            if blogDataAttending.get("data"):
                if self.data.get("userID") in blogDataAttending.get("data"):
                    iconAttending.classList.add(f"clicked")
                    iconAttending.onclick = lambda event: asyncio.ensure_future(self.attendingBtnRemove(event, blogID, iconAttending))
                else:
                    iconAttending.onclick = lambda event: asyncio.ensure_future(self.attendingBtnAdd(event, blogID, iconAttending))
            else:
                iconAttending.onclick = lambda event: asyncio.ensure_future(self.attendingBtnAdd(event, blogID, iconAttending))
                
        attendingNumber = document.createElement("span")
        attendingNumber.id = f"blog-attending-count-{blogID}"
        attendingNumber.onclick = lambda event: asyncio.ensure_future(self.listAttendingUser(event, blogID))
        
        if blogDataAttending.get("data"):
            attendingNumber.innerHTML = f"attending {len(blogDataAttending.get('data'))}"
        else:
            attendingNumber.innerHTML = "attending 0"
            
        blogPostAttending.appendChild(iconAttending)
        blogPostAttending.appendChild(attendingNumber)
        
        # Maybe
        blogDataMaybe = blogData.get("maybe")

        blogPostMaybe = document.createElement("div")
        blogPostMaybe.classList.add("blog__post--like", "blog__post--footer-btn")
        
        iconMaybe = document.createElement("i")
        iconMaybe.id = f"blog-maybe-icon-{blogID}"
        
        if not self.data.get("detail"):
            iconMaybe.classList.add("fa-solid", "fa-eye-low-vision")
            if blogDataMaybe.get("data"):
                if self.data.get("userID") in blogDataMaybe.get("data"):
                    iconMaybe.classList.add(f"clicked")
                    iconMaybe.onclick = lambda event: asyncio.ensure_future(self.maybeBtnRemove(event, blogID, iconMaybe))
                else:
                    iconMaybe.onclick = lambda event: asyncio.ensure_future(self.maybeBtnAdd(event, blogID, iconMaybe))
            else:
                iconMaybe.onclick = lambda event: asyncio.ensure_future(self.maybeBtnAdd(event, blogID, iconMaybe))
        
        maybeNumber = document.createElement("span")
        maybeNumber.id = f"blog-maybe-count-{blogID}"
        maybeNumber.onclick = lambda event: asyncio.ensure_future(self.listMaybeUser(event, blogID))
        
        if blogDataMaybe.get("data"):
            maybeNumber.innerHTML = f"maybe {len(blogDataMaybe.get('data'))}"
        else:
            maybeNumber.innerHTML = "maybe 0"
            
        blogPostMaybe.appendChild(iconMaybe)
        blogPostMaybe.appendChild(maybeNumber)
        
        # Not Attending
        blogDataNotAttending = blogData.get("notAttending")

        blogPostNotAttending = document.createElement("div")
        blogPostNotAttending.classList.add("blog__post--like", "blog__post--footer-btn")
        
        iconNotAttending = document.createElement("i")
        iconNotAttending.id = f"blog-notattending-icon-{blogID}"
        
        if not self.data.get("detail"):
            iconNotAttending.classList.add("fa-solid", "fa-eye-slash")
            if blogDataNotAttending.get("data"):
                if self.data.get("userID") in blogDataNotAttending.get("data"):
                    iconNotAttending.classList.add(f"clicked")
                    iconNotAttending.onclick = lambda event: asyncio.ensure_future(self.notAttendingBtnRemove(event, blogID, iconNotAttending))
                else:
                    iconNotAttending.onclick = lambda event: asyncio.ensure_future(self.notAttendingBtnAdd(event, blogID, iconNotAttending))
            else:
                iconNotAttending.onclick = lambda event: asyncio.ensure_future(self.notAttendingBtnAdd(event, blogID, iconNotAttending))
        
        notAttendingNumber = document.createElement("span")
        notAttendingNumber.id = f"blog-notattending-count-{blogID}"
        notAttendingNumber.onclick = lambda event: asyncio.ensure_future(self.listNotAttendingUser(event, blogID))
        
        if blogDataNotAttending.get("data"):
            notAttendingNumber.innerHTML = f"notattending {len(blogDataNotAttending.get('data'))}"
        else:
            notAttendingNumber.innerHTML = "notattending 0"
            
        blogPostNotAttending.appendChild(iconNotAttending)
        blogPostNotAttending.appendChild(notAttendingNumber)

        # Comment
        blogPostComment = document.createElement("div")
        blogPostComment.classList.add("blog__post--comment", "blog__post--footer-btn")
        blogPostComment.id = f"blog__post--comment"
        
        blogDataComment = blogData.get("reply")

        iconComment = document.createElement("i")
        iconComment.id = f"blog__comments--icon-{blogID}"
                
        if not self.data.get("detail"):
            iconComment.classList.add("fa-solid", "fa-comment")
            if blogDataComment.get("data"):
                iconComment.onclick = lambda event: asyncio.ensure_future(self.listCommentUser(event, blogDataComment, blogID))
            else:
                iconComment.onclick = lambda _: self.listNoComment(blogID)
                        
        blogPostComment.appendChild(iconComment)
        
        commentText = document.createElement("span")
        commentText.id = f"blog__comments--count-{blogID}"
        
        blogPostReplyCount = blogData.get("reply")
        if blogPostReplyCount.get("data"):
            commentText.innerHTML = f"{len(blogPostReplyCount.get('data'))} comments"
        else:
            commentText.innerHTML = "0 comment"

        blogPostComment.appendChild(commentText)

        blogPostFooter.appendChild(blogPostAttending)
        blogPostFooter.appendChild(blogPostMaybe)
        blogPostFooter.appendChild(blogPostNotAttending)
        blogPostFooter.appendChild(blogPostComment)

        blogPost.appendChild(blogPostHeader)
        blogPost.appendChild(blogPostField)
        blogPost.appendChild(blogPostFooter)
        
        self.blogPostBox.appendChild(blogPost)
        
        elementLoader = document.querySelector(".element__loader--box")
        self.blogPostBox.removeChild(elementLoader)

    async def getListMembers(self):
        try:
            response = await pyfetch(
                url=f"/user/getSortedIdByFollower", 
                method='GET',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                return data
        except Exception as e:
            print(e)

    async def loadMembers(self, memberID):
        self.blogCommunitiesList = document.querySelector("#blog__communities--list")

        memberDetail = await self.getUserDetail(memberID)
        
        blogCommunitiesPeople = document.createElement("div")
        blogCommunitiesPeople.classList.add("blog__communities--people")

        blogCommunitiesDetais = document.createElement("div")
        blogCommunitiesDetais.classList.add("blog__communities--details")

        blogCommunitiesName = document.createElement("a")
        blogCommunitiesName.classList.add("blog__communities--name")
        blogCommunitiesName.innerHTML = f"{memberDetail.get('username')}"
        blogCommunitiesName.href = f"/userInfo/{memberID}"

        blogCommunitiesFollower = document.createElement("div")
        blogCommunitiesFollower.classList.add("blog__communities--follower")
        blogCommunitiesFollower.id = f"blog__communities--follower-{memberID}"
        
        followerData = memberDetail.get('follower')
        
        if followerData.get("data"):
            followerCount = followerData.get("data")
            blogCommunitiesFollower.innerHTML = f"{len(followerCount)} followers"
        else:
            blogCommunitiesFollower.innerHTML = f"0 follower"

        blogCommunitiesDetais.appendChild(blogCommunitiesName)
        blogCommunitiesDetais.appendChild(blogCommunitiesFollower)

        blogCommunitiesFollowBtn = document.createElement("div")
        blogCommunitiesFollowBtn.classList.add("blog__communities--follow-btn")

        if not self.data.get("detail"):
            followBtn = document.createElement("p")
            followBtn.id = f"follow-btn-{memberID}"
            
            if self.data.get("following").get("data") and memberDetail.get("userID") in self.data.get("following").get("data"):
                followBtn.innerHTML = "Following"
                followBtn.onclick = lambda event: asyncio.ensure_future(self.unfollow(event, memberID))
            else: 
                followBtn.innerHTML = "Follow"
                followBtn.onclick = lambda event: asyncio.ensure_future(self.follow(event, memberID))

            blogCommunitiesFollowBtn.appendChild(followBtn)

        blogCommunitiesPeople.appendChild(blogCommunitiesDetais)
        blogCommunitiesPeople.appendChild(blogCommunitiesFollowBtn)

        self.blogCommunitiesList.appendChild(blogCommunitiesPeople)

    async def follow(self, event, memberID):
        event.preventDefault()
        try:
            response = await pyfetch(
                url=f"/user/follow?followingID={memberID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                
                followerCount = document.querySelector(f"#blog__communities--follower-{memberID}")
                count = followerCount.innerHTML
                countNum = count.split()[0]
                countNum = int(countNum) + 1
                followerCount.innerHTML = f"{countNum} followers"
                
                followBtnClicked = document.querySelector(f"#follow-btn-{memberID}")
                followBtnClicked.innerHTML = "Following"
                followBtnClicked.onclick = lambda event: asyncio.ensure_future(self.unfollow(event, memberID))
                self.followedBox.classList.remove("hidden")
                await asyncio.sleep(2)
                self.followedBox.classList.add("hidden")
                return data
        except Exception as e:
            print(e)
    
    async def unfollow(self, event, memberID):
        event.preventDefault()
        try:
            response = await pyfetch(
                url=f"/user/unfollow?followingID={memberID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                
                followerCount = document.querySelector(f"#blog__communities--follower-{memberID}")
                count = followerCount.innerHTML
                countNum = count.split()[0]
                countNum = int(countNum) - 1
                countCheck = f"0 follower" if countNum == 0 else f"{countNum} followers"
                followerCount.innerHTML = countCheck
                
                followBtnClicked = document.querySelector(f"#follow-btn-{memberID}")
                followBtnClicked.innerHTML = "Follow"
                followBtnClicked.onclick = lambda event: asyncio.ensure_future(self.follow(event, memberID))
                self.unFollowedBox.classList.remove("hidden")
                await asyncio.sleep(2)
                self.unFollowedBox.classList.add("hidden")
                return data
        except Exception as e:
            print(e)

if __name__ == "__main__":
    w = BlogWidget("blog")
    w.initializeWidget()
    w2 = LoadBlogWidget("blog")
    w2.initializeWidget()
    