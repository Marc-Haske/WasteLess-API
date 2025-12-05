from supabase import Client
from app.core.security import hash_password
from app.models.schemas import UserCreate

class UserRepository:
    def __init__(self, client: Client):
        self.client = client

    def create_user(self, user: UserCreate):
        password_hash = hash_password(user.password)
        response = (
            self.client.table("users")
            .insert({
                "username": user.username,
                "email": user.email,
                "password_hash": password_hash,
            })
            .execute()
        )
        return response.data

    def get_user_by_username(self, username: str):
        response = (
            self.client.table("users")
            .select("*")
            .eq("username", username)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None
