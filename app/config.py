from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os

# Robustly find .env if it exists
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir) # backend/
env_path = os.path.join(root_dir, ".env")

if os.path.exists(env_path):
    load_dotenv(env_path)

class Settings(BaseSettings):
    # Cloudflare R2
    cloudflare_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""
    r2_endpoint: str = ""
    aws_region: str = ""

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""

    # Database (Legacy/Optional)
    database_url: str = ""

    # CORS
    allowed_origins: str = "http://localhost:3000", "https://learnify-dev-rosy.vercel.app"

    class Config:
        env_file = env_path if os.path.exists(env_path) else None
        case_sensitive = False
        extra = "ignore" 

@lru_cache()
def get_settings():
    return Settings()
