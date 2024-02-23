import js
from pyscript import document
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
    def drawWidget(self):
        pass
    
class ConcreteWidget(AbstractWidget):
    def __init__(self, element_id):
        super().__init__(element_id)

    def drawWidget(self):
        print(self.element_id)
        self.form_element = document.querySelector("#submit__btn")
        self.form_element.onclick = self.submitForm

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
                document.location.href = "/"
        except:
            return None

if __name__ == "__main__":
    w = ConcreteWidget("signin__form")
    w.drawWidget()