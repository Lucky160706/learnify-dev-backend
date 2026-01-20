import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

print("🔍 Testing Supabase connection...")

try:
    # Test connection
    response = (
        supabase.table("planets")
        .select("*")
        .execute()
    )
    # response = supabase.table("auth.users").select("*").execute()
    print("✅ Connection successful!")
    print("Users:", response.data)
except Exception as e:
    print(f"❌ Failed to connect: {e}")