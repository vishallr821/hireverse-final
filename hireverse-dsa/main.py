from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
import docker

from db.database import create_all_tables
from db import seed
from api.routes import dsa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # a. Call create_all_tables
    logger.info("Creating database tables...")
    await create_all_tables()
    
    # b. Call run_seed
    logger.info("Seeding database...")
    await seed.run_seed()
    
    # c. Try to pull Docker images
    try:
        client = docker.from_env()
        client.ping()
        logger.info("Docker daemon found. Pulling execution images...")
        try:
            client.images.pull("python:3.11-slim")
            client.images.pull("eclipse-temurin:17-jre")
            logger.info("Docker images ready.")
        except Exception as pull_err:
            logger.warning(f"Failed to pull images, but Docker is running: {pull_err}")
    except Exception as e:
        logger.warning(f"Docker not found — using subprocess fallback. Error: {e}")
        
    yield

app = FastAPI(title="HireVerse DSA Evaluation Module", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Templates setup
templates = Jinja2Templates(directory="web/templates")

# Include API routers
app.include_router(dsa.router, prefix="/dsa", tags=["dsa"])

# Page Serving GET Routes
@app.get("/")
async def root():
    return RedirectResponse(url="/problems")


@app.get("/problems", response_class=HTMLResponse)
async def problems_page(request: Request):
    return templates.TemplateResponse("problems.html", {"request": request})

@app.get("/dsa/challenge/{problem_id}", response_class=HTMLResponse)
async def challenge_page(request: Request, problem_id: int):
    return templates.TemplateResponse("challenge.html", {"request": request, "problem_id": problem_id})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
