import js
from pyscript import window, document
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch
from abc import ABC, abstractmethod

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
            for i, v in enumerate(self.allFiles):
                print(i, v, end="\n")
                
        # self.listSection.style.display = "flex"
                
    
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
        for i, v in enumerate(self.allFiles):
            print(i, v, end="\n")
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
                print(data)
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
        self.allFiles = []
        self.counter = 0
        self.listSection.style.display = "none"
        self.assetsList.innerHTML = ""
    
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
        
    async def onLoad(self):
        self.data = await self.getUserInfo()
        print(self.data)
        
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
    
    def loadBlog(self):
        pass

if __name__ == "__main__":
    w = BlogWidget("blog")
    w.initializeWidget()
    w2 = LoadBlogWidget("blog")
    w2.initializeWidget()
