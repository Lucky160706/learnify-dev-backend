from supabase import create_client, Client
from app.config import get_settings
from functools import lru_cache

settings = get_settings()

@lru_cache()
def get_supabase() -> Client:
    """Create and return a cached Supabase client instance (singleton)"""
    url: str = settings.supabase_url
    key: str = settings.supabase_key
    return create_client(url, key)

# Lazy-loaded client - will be created on first access
def get_client() -> Client:
    """Get the Supabase client (lazy-loaded)"""
    return get_supabase()
