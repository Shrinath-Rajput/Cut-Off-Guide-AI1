import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, get_db

from app.routes import auth, users, admin, colleges, cutoffs

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="CutoffGrid API",
    description="Backend API for Cutoff Guide AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(colleges.router)
app.include_router(cutoffs.router)

@app.get("/api/health", tags=["Health"])
async def health_check():
    db = get_db()
    db_status = "ok" if db is not None else "disconnected"
    return {
        "status": "ok",
        "database": db_status
    }
