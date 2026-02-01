
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print(f"Connecting to: {url}")

try:
    print("\nTesting 'quizzes' table:")
    res = supabase.table("quizzes").select("count", count="exact").limit(1).execute()
    print(f"Success: {res.count} quizzes found")
except Exception as e:
    print(f"Error 'quizzes': {e}")

try:
    print("\nTesting 'quiz_attempts' table:")
    res = supabase.table("quiz_attempts").select("count", count="exact").limit(1).execute()
    print(f"Success: {res.count} attempts found")
except Exception as e:
    print(f"Error 'quiz_attempts': {e}")

try:
    print("\nTesting 'user' table:")
    res = supabase.table("user").select("count", count="exact").limit(1).execute()
    print(f"Success: {res.count} users found")
except Exception as e:
    print(f"Error 'user': {e}")

try:
    print("\nTesting 'users' table (alternative name):")
    res = supabase.table("users").select("count", count="exact").limit(1).execute()
    print(f"Success: {res.count} users (alternative) found")
except Exception as e:
    print(f"Error 'users': {e}")
