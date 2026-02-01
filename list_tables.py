
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print(f"Connecting to: {url}")

try:
    # This is a bit hacky for PostgREST but sometimes works to see schema
    res = supabase.rpc("get_tables", {}).execute()
    print("Tables via RPC:", res.data)
except Exception as e:
    print(f"Error RPC: {e}")

try:
    # Try to query the information_schema via a trick if possible, 
    # but PostgREST usually doesn't expose it.
    # Alternatively, try to see what hints it gives for a non-existent table
    res = supabase.table("non_existent").select("*").execute()
except Exception as e:
    print(f"\nHint from error: {e}")
