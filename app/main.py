from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from app.config import get_settings
# from app.database import engine, Base
from app.routers import courses, chapters, lessons
import time

settings = get_settings()

# Supabase does not need table creation via SQLAlchemy
print("✅ Server starting with Supabase Client enabled")

app = FastAPI(
    title="Course Management API",
    description="API for managing courses, chapters, and lessons",
    version="1.0.0",
)

# CORS
origins = [o.strip() for o in settings.allowed_origins.split(",")] if settings.allowed_origins else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(courses.router)
app.include_router(chapters.router)
app.include_router(lessons.router)


@app.get("/")
def root():
    return {"message": "Course Management API", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
