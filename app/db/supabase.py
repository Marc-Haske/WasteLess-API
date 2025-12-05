from supabase import create_client, Client
from app.core.config import SUPABASE_URL, SUPABASE_KEY

_supabase_client: Client | None = None

def get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client
