from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

assets = Jinja2Templates(directory="../assets/")
pages = Jinja2Templates(directory="../pages/")

# Assets
app.mount("/assets",
          StaticFiles(directory="../assets"), name="assets-static")

# Global
app.mount("/global-static",
          StaticFiles(directory="../global"), name="global-static")

# Home
app.mount("/main-static",
          StaticFiles(directory="../pages/00-home"), name="main-static")


@app.get("/", response_class=HTMLResponse, tags=["website"])
async def index(request: Request):
    return pages.TemplateResponse("00-home/index.html", {"request": request})
