from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Create engine - Use DATABASE_URL, not SUPABASE_URL
db_url = settings.database_url if settings.database_url else "postgresql://localhost/dummy"
engine = create_engine(
    db_url,
    pool_pre_ping=True,        # Test connection before using
    pool_size=10,               # Connection pool size
    max_overflow=20,            # Max connections when pool is full
    pool_recycle=3600,          # Recycle connections every hour
    echo=False,                 # Set True to see SQL queries (for debugging)
    connect_args={
        "connect_timeout": 10,
        "options": "-c timezone=utc"
    } 
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Dependency
def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
