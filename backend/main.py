from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from blog import router as blog_router
from account_management import router as accounte_management_router
from account_management import *

app = FastAPI()

# Routers
# =============================================================================

app.include_router(blog_router)
app.include_router(accounte_management_router)

# =============================================================================

assets = Jinja2Templates(directory="../assets/")
pages = Jinja2Templates(directory="../pages/")

# Assets
# =============================================================================

app.mount("/assets",
          StaticFiles(directory="../assets"), name="assets-static")

app.mount("/global-static",
          StaticFiles(directory="../global"), name="global-static")

app.mount("/main-static",
          StaticFiles(directory="../pages/00-home"), name="main-static")

app.mount("/signin-static",
          StaticFiles(directory="../pages/01-signin"), name="signin-static")

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

# =============================================================================
