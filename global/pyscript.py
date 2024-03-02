import js
from pyscript import document
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch
from abc import ABC, abstractmethod
import asyncio

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
    
class UserWidget(AbstractWidget):
    def __init__(self, element_id):
        super().__init__(element_id)
        
    def initializeWidget(self):
        self.navBoxGuest = document.querySelector("#nav__box--guest")
        self.navBoxUser = document.querySelector("#nav__box--user")
        asyncio.ensure_future(self.getUserInfo())
        
    async def getUserInfo(self):
        try:
            response = await pyfetch(
                url="/user/info", 
                method='GET', 
                headers={'Content-Type': 'application/json'}
            )

            if response.ok:
                data = await response.json()
                print(data)
                if data.get('username'):
                    self.navBoxGuest.classList.add("hidden")
                    self.navBoxUser.classList.remove("hidden")
                else:
                    self.navBoxGuest.classList.remove("hidden")
                    self.navBoxUser.classList.add("hidden")
        except Exception as e:
            print(e)

if __name__ == "__main__":
    w = UserWidget("navigation")
    w.initializeWidget()