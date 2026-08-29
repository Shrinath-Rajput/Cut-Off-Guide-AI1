import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, get_db
from app.routes import assistant, auth, users, admin, colleges, cutoffs, profile, saved, contact

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    try:
        if get_db() is not None:
            await admin.ensure_admin_account(get_db())
    except Exception as e:
        print("Admin account setup skipped (MongoDB offline):", e)
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="CutoffGrid API",
    description="Backend API for Cutoff Guide AI",
    version="1.0.0",
    lifespan=lifespan
)

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# CORS configuration
allowed_origins = list(dict.fromkeys((settings.CORS_ORIGINS or []) + [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:5176",
    "http://127.0.0.1:3000",
]))
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(colleges.router)
app.include_router(cutoffs.router)
app.include_router(profile.router)
app.include_router(saved.router)
app.include_router(assistant.router)
app.include_router(contact.router)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    import traceback
    traceback.print_exc()
    origin = request.headers.get("origin") or "*"
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": str(exc)},
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.get("/api/health", tags=["Health"])
async def health_check():
    db = get_db()
    db_status = "ok" if db is not None else "disconnected"
    return {
        "status": "ok",
        "database": db_status
    }

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "service": "CutoffGrid API",
        "docs": "/docs"
    }
