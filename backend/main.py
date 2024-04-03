from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from blog import router as blog_router
from account_management import router as accounte_management_router
from media_response import router as media_response_router

app = FastAPI()

# Routers
# =============================================================================

app.include_router(blog_router)
app.include_router(accounte_management_router)
app.include_router(media_response_router)

# =============================================================================

assets = Jinja2Templates(directory="../assets/")
pages = Jinja2Templates(directory="../pages/")

# Assets
# =============================================================================

app.mount("/assets",
          StaticFiles(directory="../assets"), name="assets-static")

app.mount("/uploads",
          StaticFiles(directory="../backend/uploads"), name="uploads-static")

app.mount("/global-static",
          StaticFiles(directory="../global"), name="global-static")

app.mount("/main-static",
          StaticFiles(directory="../pages/00-home"), name="main-static")

app.mount("/signin-static",
          StaticFiles(directory="../pages/01-signin"), name="signin-static")

app.mount("/signup-static",
          StaticFiles(directory="../pages/02-signup"), name="signup-static")

app.mount("/resetpassword-static",
          StaticFiles(directory="../pages/03-resetpassword"), name="resetpassword-static")

app.mount("/blog-static",
          StaticFiles(directory="../pages/04-blog"), name="blog-static")

app.mount("/setpassword-static",
          StaticFiles(directory="../pages/05-setpassword"), name="setpassword-static")

app.mount("/userinfo-static", 
          StaticFiles(directory="../pages/06-userinfo"), name="userinfo-static")

app.mount("/prayers-static", 
          StaticFiles(directory="../pages/prayers"), name="prayers-static")

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

@app.get("/resetPassword", response_class=HTMLResponse, tags=["website"])
async def resetPasswordPage(request: Request):
    return pages.TemplateResponse("03-resetpassword/resetpassword.html", {"request": request})

@app.get("/lotusBlog", response_class=HTMLResponse, tags=["website"])
async def blogPage(request: Request):
    return pages.TemplateResponse("04-blog/blog.html", {"request": request})

@app.get("/setpassword/{token}", response_class=HTMLResponse, tags=["website"])
async def resetPasswordPage(request: Request, token: str):
    return pages.TemplateResponse("05-setpassword/setpassword.html", {"request": request, "token": token})

@app.get("/userInfo", response_class=HTMLResponse, tags=["website"])
async def userInfoPage(request: Request):
    return pages.TemplateResponse("06-userinfo/userinfo.html", {"request": request})

# =============================================================================


# Prayers
# =============================================================================

@app.get("/prayers/01", response_class=HTMLResponse, tags=["prayers"])
async def index(request: Request):
    return pages.TemplateResponse("prayers/01/01.html", {"request": request})


@app.get("/prayers/02", response_class=HTMLResponse, tags=["prayers"])
async def index(request: Request):
    return pages.TemplateResponse("prayers/02/02.html", {"request": request})


@app.get("/prayers/03", response_class=HTMLResponse, tags=["prayers"])
async def index(request: Request):
    return pages.TemplateResponse("prayers/03/03.html", {"request": request})


@app.get("/prayers/04", response_class=HTMLResponse, tags=["prayers"])
async def index(request: Request):
    return pages.TemplateResponse("prayers/04/04.html", {"request": request})


@app.get("/prayers/05", response_class=HTMLResponse, tags=["prayers"])
async def index(request: Request):
    return pages.TemplateResponse("prayers/05/05.html", {"request": request})


@app.get("/prayers/06", response_class=HTMLResponse, tags=["prayers"])
async def index(request: Request):
    return pages.TemplateResponse("prayers/06/06.html", {"request": request})

@app.get("/prayers/07", response_class=HTMLResponse, tags=["prayers"])
async def index(request: Request):
    return pages.TemplateResponse("prayers/07/07.html", {"request": request})


@app.get("/prayers/08", response_class=HTMLResponse, tags=["prayers"])
async def index(request: Request):
    return pages.TemplateResponse("prayers/08/08.html", {"request": request})


@app.get("/prayers/09", response_class=HTMLResponse, tags=["prayers"])
async def index(request: Request):
    return pages.TemplateResponse("prayers/09/09.html", {"request": request})


@app.get("/prayers/10", response_class=HTMLResponse, tags=["prayers"])
async def index(request: Request):
    return pages.TemplateResponse("prayers/10/10.html", {"request": request})


@app.get("/prayers/11", response_class=HTMLResponse, tags=["prayers"])
async def index(request: Request):
    return pages.TemplateResponse("prayers/11/11.html", {"request": request})


@app.get("/prayers/12", response_class=HTMLResponse, tags=["prayers"])
async def index(request: Request):
    return pages.TemplateResponse("prayers/12/12.html", {"request": request})

# =============================================================================
