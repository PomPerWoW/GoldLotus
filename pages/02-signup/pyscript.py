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
    
class SignUpWidget(AbstractWidget):
    def __init__(self, element_id):
        super().__init__(element_id)
    
    def initializeWidget(self):
        self.form_element = document.querySelector("#submit__btn")
        self.form_element.onclick = self.submitForm
        
    async def submitForm(self, event):
        event.preventDefault()
        username = document.querySelector("#username").value
        email = document.querySelector("#email").value
        password = document.querySelector("#password").value
        try:
            response = await pyfetch(
                url=f"/user/signUp/?username={username}&email={email}&password={password}",
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                data = await response.json()
                print(data)
                js.alert("signup")
                window.location.href = "/"
        except Exception as e:
            print(e)

if __name__ == "__main__":
    w = SignUpWidget("signup__form")
    w.initializeWidget()