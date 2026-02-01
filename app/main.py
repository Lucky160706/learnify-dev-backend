from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from app.config import get_settings
# from app.database import engine, Base
from app.routers import courses, chapters, lessons, quiz, cron

settings = get_settings()

# Supabase does not need table creation via SQLAlchemy
print("✅ Server starting with Supabase Client enabled")

app = FastAPI(
    title="Course Management API",
    description="API for managing courses, chapters, and lessons",
    version="1.0.0",
)

# CORS
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://0.0.0.0:3000",
    "http://0.0.0.0:5173",
    "https://learnify-dev-rosy.vercel.app",
    "https://www.learnify.live",
    "https://learnify.live"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(courses.router)
app.include_router(chapters.router)
app.include_router(lessons.router)
app.include_router(quiz.router)
app.include_router(cron.router)


@app.get("/")
def root():
    return {"message": "Course Management API", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
