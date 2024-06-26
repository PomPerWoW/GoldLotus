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
        self.addMediaBtn = document.querySelector("#add-media-btn")
        self.removeMediaBtn = document.querySelector("#remove-media-btn")
        self.createPostAssets = document.querySelector(".blog__create-post--assets")
        self.dropArea = document.querySelector(".blog__create-post--assets-draganddrop")
        self.listSection = document.querySelector(".blog__create-post--assets-list")
        self.assetsList = document.querySelector(".assets-list")
        self.fileSelector = document.querySelector(".blog__create-post--assets-btn-selector")
        self.fileSelectorInput = document.querySelector(".blog__create-post--assets-btn-input")
        self.mediaFiles = document.querySelector("#media")
        self.blogCreateBtn = document.querySelector("#submit__btn")
        self.resetBtn = document.querySelector("#reset__btn")
        self.successBox = document.querySelector("#success__box")
        self.errorBox = document.querySelector("#error__box")
        self.statusBox1 = document.querySelector("#error__box--btn")
        
        self.addMediaBtn.onclick = lambda e: self.handleAddMediaBtn(e)
        self.removeMediaBtn.onclick = lambda e: self.handleRemoveMediaBtn(e)
        self.fileSelector.onclick = lambda _: self.fileSelectorInput.click()
        self.fileSelectorInput.onchange = lambda e: self.handleFileInputChange(e)
        self.dropArea.ondragover = lambda e: self.handleDragOver(e)
        self.dropArea.ondragleave = lambda _: self.handleDragLeave()
        self.dropArea.ondrop = lambda e: self.handleDrop(e)
        self.blogCreateBtn.onclick = self.uploadFile
        self.resetBtn.onclick = self.resetInput
        self.statusBox1.onclick = lambda e: self.removeStatus(e)
    
    def handleAddMediaBtn(self, event):
        event.preventDefault()
        document.querySelector("#media").value = ""
        self.allFiles = []
        self.counter = 0
        self.listSection.style.display = "none"
        self.assetsList.innerHTML = ""
        self.addMediaBtn.style.display = "none"
        self.removeMediaBtn.style.display = "block"
        self.createPostAssets.style.display = "flex"
    
    def handleRemoveMediaBtn(self, event):
        event.preventDefault()
        document.querySelector("#media").value = ""
        self.allFiles = []
        self.counter = 0
        self.listSection.style.display = "none"
        self.assetsList.innerHTML = ""
        self.addMediaBtn.style.display = "block"
        self.removeMediaBtn.style.display = "none"
        self.createPostAssets.style.display = "none"

    def handleFileInputChange(self, event):
        event.preventDefault()
        for file in js.Array.from_(self.fileSelectorInput.files):
            if self.typeValidation(file.type):
                self.allFiles.append(file)
                self.displayFile(file)
            else:
                print("Invalid file type")

    def handleDragOver(self, event):
        event.preventDefault()
        for item in js.Array.from_(event.dataTransfer.items):
            if self.typeValidation(item.type):
                self.dropArea.classList.add('drag-over-effect')
                
    def handleDragLeave(self):
        self.dropArea.classList.remove('drag-over-effect')
        
    def handleDrop(self, event):
        event.preventDefault()
        self.dropArea.classList.remove('drag-over-effect')

        if event.dataTransfer.items:
            for item in js.Array.from_(event.dataTransfer.items):
                if item.kind == 'file':
                    file = item.getAsFile()
                    if self.typeValidation(file.type):
                        self.allFiles.append(file)
                        self.displayFile(file)
        else:
            for file in js.Array.from_(event.dataTransfer.files):
                if self.typeValidation(file.type):
                    pass

    def typeValidation(self, fileType):
        validTypes = ['image/png', 'image/jpeg', 'video/mp4']
        return fileType in validTypes
    
    def deleteElement(self, del_id):
        delIdSplit = del_id.split("-")
        indexToDelete = int(delIdSplit[2])
        delElement = document.querySelector(f"#assets-element-{indexToDelete}")

        if delElement:
            self.allFiles[indexToDelete] = 0
            delElement.parentNode.removeChild(delElement)
            
    def displayFile(self, file):
        self.listSection.style.display = "flex"
        
        assetsElement = document.createElement("div")
        assetsElement.classList.add("assets-element")
        assetsElement.id = f"assets-element-{self.counter}"
        
        col1 = document.createElement("div")
        col1.classList.add("col1")
        col2 = document.createElement("div")
        col2.classList.add("col2")
        
        iconFile = document.createElement("i")
        iconFile.classList.add("fa-solid", "fa-file")
        
        fileName = document.createElement("div")
        fileName.classList.add("file-name")
        fileName.innerHTML = f"{file.name}"

        col1.appendChild(iconFile)
        col1.appendChild(fileName)

        fileSize = document.createElement("div")
        fileSize.classList.add("file-size")
        fileSize.innerHTML = f"{(file.size / (1024 * 1024)):.2f} MB"
        
        deleteButton = document.createElement("a")
        deleteButton.id = f"assets-delete-{self.counter}"
        
        iconCross = document.createElement("i")
        iconCross.classList.add("fa-solid", "fa-xmark")
        
        deleteButton.appendChild(iconCross)
        deleteButton.onclick = lambda _: self.deleteElement(deleteButton.id)

        col2.appendChild(fileSize)
        col2.appendChild(deleteButton)

        assetsElement.appendChild(col1)
        assetsElement.appendChild(col2)
        
        self.assetsList.appendChild(assetsElement)
        self.counter += 1
    
    def updateFile(self):
        self.tempFiles = []
        for i in range(len(self.allFiles)):
            if self.allFiles[i] != 0:
                self.tempFiles.append(self.allFiles[i])
        self.allFiles = self.tempFiles
        del self.tempFiles

    async def uploadFile(self, event):
        event.preventDefault()
        self.updateFile()
        form_data = window.FormData.new()

        for i in range(len(self.allFiles)):
            form_data.append('media', self.allFiles[i])
            
        title = document.querySelector("#title").value
        text = document.querySelector("#text").value

        try:
            urlInput = ""
            if len(self.allFiles) == 0:
                urlInput = f"/createBlog/?title={title}&text={text}"
            else:
                urlInput = f"/createBlogWithMedia/?title={title}&text={text}"
            
            response = await pyfetch(
                url=urlInput,
                method='POST',
                body=form_data,
            )

            if response.ok:
                data = await response.json()
                detail_value = data.get('detail')
                if detail_value is not None and detail_value:
                    self.errorBox.classList.remove("hidden")
                else:
                    self.successBox.classList.remove("hidden")
                    self.resetInput(event)
                    self.handleRemoveMediaBtn(event)
        except Exception as error:
            print('Error:', error)
    
    def resetInput(self, event):
        event.preventDefault()
        document.querySelector("#title").value = ""
        document.querySelector("#text").value = ""
        document.querySelector("#media").value = ""
        self.handleRemoveMediaBtn(event)
    
    def removeStatus(self, event):
        event.preventDefault()
        self.errorBox.classList.add("hidden")
    
    def printFileDetails(self, file):
        print(f"File Name: {file.name}")
        print(f"File Size: {file.size} bytes")
        print(f"File Type: {file.type}")
        print(f"Last Modified: {file.lastModified}")

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
        self.currentMyPostBlogIDSaved = 0
        self.currentFollowingBlogIDSaved = 0
        self.currentPopularBlogIDSaved = 0
        
        self.successBoxBtn.onclick = self.createNewPostSuccess
        
        # Pagination
        self.blogPagLatest = document.querySelector(".blog__pagination--latest")
        self.blogPagPopular = document.querySelector(".blog__pagination--popular")
        self.blogPagFollowing = document.querySelector(".blog__pagination--following")
        self.blogPagMypost = document.querySelector(".blog__pagination--mypost")
        # Btn
        self.blogPagLatestBtn = document.querySelector("#blog__pagination--latest")
        self.blogPagPopularBtn = document.querySelector("#blog__pagination--popular")
        self.blogPagFollowingBtn = document.querySelector("#blog__pagination--following")
        self.blogPagMypostBtn = document.querySelector("#blog__pagination--mypost")
        
        self.blogPagLatest.onclick = self.loadLatest
        self.blogPagPopularBtn.onclick = self.loadPopular
        self.blogPagFollowingBtn.onclick = self.loadFollowing
        self.blogPagMypostBtn.onclick = self.loadMyPost

        self.likedBox = document.querySelector("#liked__box")
        self.unLikedBox = document.querySelector("#unliked__box")
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
        self.blogCommunitiesList = document.querySelector("#blog__communities--list")

    async def onLoad(self):
        self.data = await self.getUserInfo()
        if self.data.get("detail") == "'NoneType' object is not subscriptable":
            self.guestUser()
        
        await self.loadLatest()
        
        self.membersList = await self.getListMembers()
        
        for i in range(len(self.membersList)):
            if self.membersList[i] != self.data.get("userID"):
                await self.loadMembers(self.membersList[i])
    
    async def createNewPostSuccess(self, event):
        event.preventDefault()
        self.successBox.classList.add("hidden")
        
        await self.loadLatest()
    
    def removeBlogPosts(self):
        blogPosts = document.querySelectorAll(".blog__post--element")
        for post in blogPosts:
            post.parentNode.removeChild(post)
    
    async def loadLatest(self, event=None, viewMore=False, notView=True):
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
        currentBlogID = self.currentLatestBlogIDSaved if self.currentLatestBlogIDSaved != 0 else self.blogLists.get("currentBlogID") - 1

        while counter < 10 and currentBlogID != 0:
            blogData = await self.loadBlog(currentBlogID)
            if blogData.get("detail") != "blog not found":
                await self.createBlog(blogData)
                counter += 1
            currentBlogID -= 1

        self.currentLatestBlogIDSaved = currentBlogID
        
        if currentBlogID != 0 and self.currentLatestBlogIDSaved != 0:
            self.createViewMore("loadLatest")
                    
    async def loadMyPost(self, event, viewMore=False, notView=True):
        if event:
            event.preventDefault()
            
        if viewMore == False:
            self.removeBlogPosts()
        
        if notView:
            self.currentMyPostBlogIDSaved = 0
        
        viewMoreElement = document.querySelector("#blog__readmore-btn")
        if viewMoreElement:
            viewMoreElement.parentNode.removeChild(viewMoreElement)
            
        userData = await self.getUserInfo()
        self.blogLists = userData.get("blog")
        if self.blogLists.get("data"):
            blogListsData = self.blogLists.get("data")
            counter = 0
            currentBlogID = self.currentMyPostBlogIDSaved if self.currentMyPostBlogIDSaved != 0 else len(blogListsData)

            while counter < 10 and currentBlogID != 0:
                blogData = await self.loadBlog(blogListsData[currentBlogID - 1])
                if blogData.get("detail") != "blog not found":
                    await self.createBlog(blogData)
                    counter += 1
                currentBlogID -= 1

            self.currentMyPostBlogIDSaved = currentBlogID
            
            if currentBlogID != 0 and self.currentMyPostBlogIDSaved != 0:
                self.createViewMore("loadMyPost")

    async def loadFollowing(self, event):
            if event:
                event.preventDefault()
                
            self.removeBlogPosts()
                
            viewMoreElement = document.querySelector("#blog__readmore-btn")
            if viewMoreElement:
                viewMoreElement.parentNode.removeChild(viewMoreElement)

            userData = await self.getUserInfo()
            userFollowing = userData.get("following")
            if userFollowing.get("data"):
                userFollowingData = userFollowing.get("data")
            
                for user in userFollowingData:
                    followingUserDetail = await self.getUserDetail(user)
                    print(followingUserDetail)

                followingUserBlog = followingUserDetail.get("blog")
                if followingUserBlog.get("data"):
                    self.blogLists = followingUserBlog.get("data")
                    
                    for i in range(len(self.blogLists)):
                        blogData = await self.loadBlog(self.blogLists[i])
                        if blogData.get("detail") != "blog not found":
                            await self.createBlog(blogData)

    async def loadPopular(self, event, viewMore=False, notView=True):
        if event:
            event.preventDefault()
            
        if viewMore == False:
            self.removeBlogPosts()
        
        if notView:
            self.currentPopularBlogIDSaved = 0
        
        viewMoreElement = document.querySelector("#blog__readmore-btn")
        if viewMoreElement:
            viewMoreElement.parentNode.removeChild(viewMoreElement)
            
        getSortedPostByLike = await self.sortedBlogByLike()
        sortedPostByLike = getSortedPostByLike[::-1]
        
        counter = 0
        currentBlogID = self.currentPopularBlogIDSaved if self.currentPopularBlogIDSaved != 0 else len(sortedPostByLike)

        while counter < 10 and currentBlogID != 0:
            blogData = await self.loadBlog(sortedPostByLike[currentBlogID - 1])
            if blogData.get("detail") != "blog not found":
                await self.createBlog(blogData)
                counter += 1
            currentBlogID -= 1

        self.currentPopularBlogIDSaved = currentBlogID
        
        if currentBlogID != 0 and self.currentPopularBlogIDSaved != 0:
            self.createViewMore("loadPopular")
                
    async def sortedBlogByLike(self):
        try:
            response = await pyfetch(
                url="/getSortedBlogByLike", 
                method='GET', 
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                return data
        except Exception as e:
            print(e)

    def createViewMore(self, blogType):
        viewMore = document.createElement("div")
        viewMore.id = "blog__readmore-btn"
        viewMore.classList.add("blog__readmore-btn")
        
        viewMoreBtn = document.createElement("p")
        viewMoreBtn.innerHTML = "View More"
        if blogType == "loadLatest":
            viewMoreBtn.onclick = lambda event: asyncio.ensure_future(self.loadLatest(event, True, False))
        elif blogType == "loadMyPost":
            viewMoreBtn.onclick = lambda event: asyncio.ensure_future(self.loadMyPost(event, True, False))
        elif blogType == "loadPopular":
            viewMoreBtn.onclick = lambda event: asyncio.ensure_future(self.loadPopular(event, True, False))
        
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
                url=f"/getBlog/?blogID={index}", 
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
                url=f"/getCurrentBlogID/", 
                method='GET',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                return data
        except Exception as e:
            print(e)
    
    async def loadMedia(self, index):
        try:
            response = await pyfetch(
                url=f"/media/?mediaID={index}", 
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
    
    async def checkAssets(self, blogPostAssets, assetsList):
        for i in range(len(assetsList)):
            assetUpload = await self.loadMedia(assetsList[i])
            assetUploadSplit = assetUpload.split(".")
            if assetUploadSplit[1] == "mp4":
                blogAssetsVideo = document.createElement("video")
                blogAssetsVideo.setAttribute("height", "200")
                blogAssetsVideo.setAttribute("controls", "")
                blogAssetsSource = document.createElement("source")
                blogAssetsSource.src = f"/uploads/{assetUpload}"
                blogAssetsSource.type = "video/mp4"
                blogAssetsVideo.appendChild(blogAssetsSource)
                blogPostAssets.appendChild(blogAssetsVideo)
            else:
                blogAssetsImg = document.createElement("img")
                blogAssetsImg.src = f"/uploads/{assetUpload}"
                blogPostAssets.appendChild(blogAssetsImg)

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
    
    async def likeBtnAdd(self, event, blogID, btnLiked):
        event.preventDefault()
        try:
            response = await pyfetch(
                url=f"/addLikeBlog/?blogID={blogID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()

                blogLikesCount = document.querySelector(f"#blog__likes--count-{blogID}")
                counter = blogLikesCount.innerHTML.split()[0]
                counterNew = int(counter) + 1
                
                blogLikesCount.innerHTML = f"{counterNew} likes"
                
                btnLiked.classList.add("clicked")
                btnLiked.onclick = lambda event: asyncio.ensure_future(self.likeBtnRemove(event, blogID, btnLiked))
                self.likedBox.classList.remove("hidden")
                await asyncio.sleep(2)
                self.likedBox.classList.add("hidden")
                return data
        except Exception as e:
            print(e)
        
    async def likeBtnRemove(self, event, blogID, btnLiked):
        event.preventDefault()
        try:
            response = await pyfetch(
                url=f"/removeLikeBlog/?blogID={blogID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()

                blogLikesCount = document.querySelector(f"#blog__likes--count-{blogID}")
                counter = blogLikesCount.innerHTML.split()[0]
                counterNew = int(counter) - 1
                
                blogLikesCount.innerHTML = f"{counterNew} likes"

                btnLiked.classList.remove("clicked")
                btnLiked.onclick = lambda event: asyncio.ensure_future(self.likeBtnAdd(event, blogID, btnLiked))
                self.unLikedBox.classList.remove("hidden")
                await asyncio.sleep(2)
                self.unLikedBox.classList.add("hidden")
                return data
        except Exception as e:
            print(e)
    
    async def listLikedUser(self, event, blogID):
        event.preventDefault()
        currentBlog = await self.loadBlog(blogID)
        print(currentBlog.get("like"))
    
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
                url=f"/addReplyBlog/?blogID={blogID}&text={commentText}", 
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
                url=f"/addLikeReplyBlog/?blogID={blogID}&replyIndex={commentID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()

                commentLikeCount = document.querySelector(f"#comment__likes--count-{commentID}")
                counter = commentLikeCount.innerHTML.split()[0]
                counterNew = int(counter) + 1
                
                commentLikeCount.innerHTML = f"{counterNew} likes"
                
                btnLiked.classList.add("clicked")
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
                url=f"/removeLikeReplyBlog/?blogID={blogID}&replyIndex={commentID}", 
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                commentLikeCount = document.querySelector(f"#comment__likes--count-{commentID}")
                counter = commentLikeCount.innerHTML.split()[0]
                counterNew = int(counter) - 1
                
                commentLikeCount.innerHTML = f"{counterNew} likes"

                btnLiked.classList.remove("clicked")
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
                    iconLiked.classList.add("clicked")
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
        
    def createFollowingUser(self, username, userID):
        divName = document.createElement("a")
        divName.classList.add("blog__post--username-list")
        divName.innerHTML = f"{username}'s Blogs"
        divName.href = f"/userInfo/{userID}"
        
        self.blogPostBox.appendChild(divName)
            
    async def createBlog(self, blogData):
        self.createLoad()
        
        blogID = blogData.get("blogID")
        
        userDetail = await self.getUserDetail(blogData.get("author"))
        authorName = userDetail.get("username")
        
        blogPost = document.createElement("div")
        blogPost.classList.add("blog__post", "blog__post--element")

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
        blogPostTitleH3.innerHTML = f"{blogData.get('title')}"

        blogPostTitle.appendChild(blogPostTitleH3)

        blogPostMessage = document.createElement("div")
        blogPostMessage.classList.add("blog__post--message")

        blogPostMessageP = document.createElement("p")
        blogPostMessageP.innerHTML = f"{blogData.get('text')}"

        blogPostMessage.appendChild(blogPostMessageP)

        blogPostAssets = document.createElement("div")
        blogPostAssets.classList.add("blog__post--assets")

        js.Promise.resolve(self.checkAssets(blogPostAssets, blogData.get('media'))).catch(lambda e: print(e))

        blogPostField.appendChild(blogPostTitle)
        blogPostField.appendChild(blogPostMessage)
        blogPostField.appendChild(blogPostAssets)

        blogPostFooter = document.createElement("div")
        blogPostFooter.classList.add("blog__post--footer")
        
        # Like
        blogDataLike = blogData.get("like")

        blogPostLike = document.createElement("div")
        blogPostLike.classList.add("blog__post--like", "blog__post--footer-btn")
        
        iconLiked = document.createElement("i")
        iconLiked.id = f"blog__likes--icon-{blogID}"
        
        if not self.data.get("detail"):
            iconLiked.classList.add("fa-solid", "fa-heart")
            if blogDataLike.get("data"):
                if self.data.get("userID") in blogDataLike.get("data"):
                    iconLiked.classList.add("clicked")
                    iconLiked.onclick = lambda event: asyncio.ensure_future(self.likeBtnRemove(event, blogID, iconLiked))
                else:
                    iconLiked.onclick = lambda event: asyncio.ensure_future(self.likeBtnAdd(event, blogID, iconLiked))
            else:
                iconLiked.onclick = lambda event: asyncio.ensure_future(self.likeBtnAdd(event, blogID, iconLiked))

        blogPostLike.appendChild(iconLiked)
        
        likesText = document.createElement("span")
        likesText.id = f"blog__likes--count-{blogID}"
        likesText.onclick = lambda event: asyncio.ensure_future(self.listLikedUser(event, blogID))
        
        if blogDataLike.get("data"):
            likesText.innerHTML = f"{len(blogDataLike.get('data'))} likes"
        else:
            likesText.innerHTML = "0 likes"
        
        blogPostLike.appendChild(likesText)

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

        blogPostFooter.appendChild(blogPostLike)
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
    
