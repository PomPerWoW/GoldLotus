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
        self.hidden_element_username = document.querySelector("#error_hidden_username")
        self.hidden_element_email = document.querySelector("#error_hidden_email")
        self.hidden_element_default = document.querySelector("#error_hidden_default")
        
        if not self.hidden_element_email:
            return
        
        if not self.hidden_element_default:
            return
        
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
                    
                if isinstance(data, dict):
                    detail_value = data.get('detail')
                    if detail_value is not None and detail_value == "email already exist":
                        self.hidden_element_email.classList.remove("hidden")
                    elif detail_value is not None and detail_value == "username is already taken":
                        self.hidden_element_username.classList.remove("hidden")
                    elif detail_value is not None and detail_value:
                        self.hidden_element_default.classList.remove("hidden")
                else:
                    window.location.href = "/"
        except Exception as error:
            print('Error:', error)

if __name__ == "__main__":
    w = SignUpWidget("signup__form")
    w.initializeWidget()