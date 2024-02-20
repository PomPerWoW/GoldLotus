from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

assets = Jinja2Templates(directory="../00-assets/")
pages = Jinja2Templates(directory="../02-pages/")

# Statics
# ============================================================================

# Assets
app.mount("/assets",
          StaticFiles(directory="../00-assets"), name="assets-static")

# Global
app.mount("/global-static",
          StaticFiles(directory="../01-global"), name="global-static")

# Home
app.mount("/main-static",
          StaticFiles(directory="../02-pages/00-home"), name="main-static")

# ============================================================================


# Templates
# ============================================================================

@app.get("/", response_class=HTMLResponse, tags=["website"])
async def index(request: Request):
    return pages.TemplateResponse("00-home/index.html", {"request": request})


@app.get("/signin", response_class=HTMLResponse, tags=["website"])
async def signin_page(request: Request):
    return pages.TemplateResponse("01-signin/signin.html", {"request": request})

# ============================================================================
