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
    
class SignInWidget(AbstractWidget):
    def __init__(self, element_id):
        super().__init__(element_id)

    def initializeWidget(self):
        element = self.element
        form_id = element.id
        form_class = element.classList.value
        form_action = element.getAttribute("action")
        form_method = element.getAttribute("method")

        print(f"ID: {form_id}")
        print(f"Class: {form_class}")
        print(f"Action: {form_action}")
        print(f"Method: {form_method}")
        self.form_element = document.querySelector("#submit__btn")
        self.form_element.onclick = self.submitForm
        
    # try:
    #         response = await pyfetch(
    #             url="/user/signIn/", 
    #             method='GET', 
    #             headers={'Content-Type': 'application/json'},
    #             body=js.JSON.stringify({
    #                 'key': username,
    #                 'password': password,
    #             }),
    #         )
    #         if response.ok:
    #             data = await response.json()
    #             print(data)
    #             js.alert("signin")
    #             window.location.href = "/"
    # except Exception as e:
    #     print(e) 

    async def submitForm(self, event):
        event.preventDefault()
        username = document.querySelector("#username").value
        password = document.querySelector("#password").value
        try:
            response = await pyfetch(
                url=f"/user/signIn/?key={username}&password={password}", 
                method='GET', 
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                print(data)
                js.alert("signin")
                window.location.href = "/"
        except Exception as e:
            print(e)

if __name__ == "__main__":
    w = SignInWidget("signin__form")
    w.initializeWidget()