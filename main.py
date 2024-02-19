from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

assets = Jinja2Templates(directory="00-assets/")
pages = Jinja2Templates(directory="02-pages/")


@app.get("/", response_class=HTMLResponse, tags=["website"])
async def index(request: Request):
    return pages.TemplateResponse("00-home/index.html", {"request": request})
