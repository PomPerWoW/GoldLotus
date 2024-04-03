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
        self.statusBox2 = document.querySelector("#success__box--btn")
        
        self.addMediaBtn.onclick = lambda e: self.handleAddMediaBtn(e)
        self.removeMediaBtn.onclick = lambda e: self.handleRemoveMediaBtn(e)
        self.fileSelector.onclick = lambda _: self.fileSelectorInput.click()
        self.fileSelectorInput.onchange = lambda e: self.handleFileInputChange(e)
        self.dropArea.ondragover = lambda e: self.handleDragOver(e)
        self.dropArea.ondragleave = lambda _: self.handleDragLeave()
        self.dropArea.ondrop = lambda e: self.handleDrop(e)
        self.blogCreateBtn.onclick = self.uploadFile
        self.resetBtn.onclick = self.resetInput
        self.statusBox1.onclick = lambda e: self.displayStatus(e)
        self.statusBox2.onclick = lambda e: self.displayStatus(e)
    
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
    
    def displayStatus(self, event):
        event.preventDefault()
        self.successBox.classList.add("hidden")
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
        self.blogCommunities = document.querySelector("#blog__communities")
        self.successBoxBtn = document.querySelector("#success__box--btn")
        
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
        self.blogPagMypostBtn.onclick = self.loadMyPost

        self.likedBox = document.querySelector("#liked__box")
        self.unLikedBox = document.querySelector("#unliked__box")

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

    async def onLoad(self):
        self.data = await self.getUserInfo()
        if self.data.get("detail") == "'NoneType' object is not subscriptable":
            self.guestUser()
        
        await self.loadLatest()
    
    def removeBlogPosts(self):
        blogPosts = document.querySelectorAll(".blog__post--element")
        for post in blogPosts:
            post.parentNode.removeChild(post)
    
    async def loadLatest(self, event=None):
        if event:
            event.preventDefault()
        self.removeBlogPosts()
        self.blogLists = await self.trackBlog()
        for i in range(self.blogLists.get("currentBlogID") - 1, 0, -1):
            # {'detail': 'blog not found'}
            blogData = await self.loadBlog(i)
            if blogData.get("detail") != "blog not found":
                await self.createBlog(blogData)
    
    async def loadMyPost(self, event):
        if event:
            event.preventDefault()
        self.removeBlogPosts()
        userData = await self.getUserInfo()
        self.blogLists = userData.get("blog").get("data")
        if self.blogLists:
            for i in range(len(self.blogLists) - 1, -1, -1):
                blogData = await self.loadBlog(self.blogLists[i])
                if blogData.get("detail") != "blog not found":
                    await self.createBlog(blogData)
        
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
            self.createComments(data, index, userDetail)
    
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
                
                self.likedBox.classList.remove("hidden")
                await asyncio.sleep(2)
                self.likedBox.classList.add("hidden")
                
                blogData = await self.loadBlog(blogID)
                blogDataComment = blogData.get("reply")
                
                await self.listCommentUser(event, blogDataComment, blogID)
                
                return data
        except Exception as e:
            print(e)
    
    def createComments(self, commentData, commentID, userDetail):
        # { commentData
            # 'author': '0000000000000', 
            # 'text': 'Amazing!', 
            # 'edited': False, 
            # 'timestamp': 
            # '2024-04-02T00:47:39.119881', 
            # 'like': {}
            # }'
        print(commentData, commentID)
        
        userCommentsPerson = document.createElement("div")
        userCommentsPerson.classList.add("user__comments--person")
        userCommentsPerson.id = f"user__comments--person-{commentID}"
        
        userCommentsUpper = document.createElement("div")
        userCommentsUpper.classList.add("user__comments--upper")
        
        userCommentsName = document.createElement("div")
        userCommentsName.classList.add("user__comments--name")
        userCommentsName.innerHTML = f"{userDetail.get('username')}"

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

        userCommentsLike = document.createElement("div")
        userCommentsLike.classList.add("user__comments--like")

        likeIcon = document.createElement("i")
        likeIcon.classList.add("fa-solid", "fa-heart")

        likeSpan = document.createElement("span")
        likeSpan.id = f"comment__likes--count-{commentID}"
        likeSpan.innerHTML = "0 likes"

        userCommentsLike.appendChild(likeIcon)
        userCommentsLike.appendChild(likeSpan)

        userCommentsPerson.appendChild(userCommentsUpper)
        userCommentsPerson.appendChild(userCommentsText)
        userCommentsPerson.appendChild(userCommentsLike)
        
        self.userComponentBody.appendChild(userCommentsPerson)
            
    async def createBlog(self, blogData):
        self.createLoad()
        
        blogID = blogData.get("blogID")
        
        userDetail = await self.getUserDetail(blogData.get("author"))
        authorName = userDetail.get("username")
        
        blogPost = document.createElement("div")
        blogPost.classList.add("blog__post", "blog__post--element")

        blogPostHeader = document.createElement("div")
        blogPostHeader.classList.add("blog__post--header")
        
        blogPostUsername = document.createElement("div")
        blogPostUsername.classList.add("blog__post--username")    
        blogPostUsername.innerHTML = f"{authorName}"

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
        iconComment.id = f"blog__likes--icon-{blogID}"
                
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

if __name__ == "__main__":
    w = BlogWidget("blog")
    w.initializeWidget()
    w2 = LoadBlogWidget("blog")
    w2.initializeWidget()
    
