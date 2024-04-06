from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from blog import router as blog_router
from account_management import router as accounte_management_router
from account_management import *
from media_response import router as media_response_router
from event import router as event_router
from map import router as map_router

app = FastAPI()

# Routers
# =============================================================================

app.include_router(blog_router)
app.include_router(accounte_management_router)
app.include_router(media_response_router)
app.include_router(event_router)
app.include_router(map_router)

# =============================================================================

assets = Jinja2Templates(directory="../assets/")
pages = Jinja2Templates(directory="../pages/")

# Assets
# =============================================================================

app.mount("/assets", StaticFiles(directory="../assets"), name="assets-static")
app.mount("/global-static", StaticFiles(directory="../global"), name="global-static")
app.mount("/main-static", StaticFiles(directory="../pages/00-home"), name="main-static")

# =============================================================================

# Templates
# =============================================================================

@app.get("/", response_class=HTMLResponse, tags=["website"])
async def index(request: Request):
    return pages.TemplateResponse("00-home/index.html", {"request": request})

@app.get("/signIn", response_class=HTMLResponse, tags=["website"])
async def signInPage(request: Request):
    return pages.TemplateResponse("01-signin/signin.html", {"request": request})

@app.get("/signUp", response_class=HTMLResponse, tags=["website"])
async def signUpPage(request: Request):
    return pages.TemplateResponse("02-signup/signup.html", {"request": request})

@app.get("/testBlog", response_class=HTMLResponse, tags=["website"])
async def testBlog(request: Request):
    return pages.TemplateResponse("upload_test.html", {"request": request})

@app.get("/testPrayers", response_class=HTMLResponse, tags=["website"])
async def testPrayers(request: Request):
    return pages.TemplateResponse("prayers/01/01.html", {"request": request})

# =============================================================================
