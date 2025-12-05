from fastapi import HTTPException
from app.core.security import verify_password, create_access_token
from app.models.schemas import UserCreate, UserLogin
from app.repositories.users import UserRepository

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def create_user(self, user: UserCreate):
        if self.user_repo.get_user_by_username(user.username):
            raise HTTPException(status_code=409, detail="Username already exists")
        data = self.user_repo.create_user(user)
        if not data:
            raise HTTPException(status_code=500, detail="Error creating user")
        return data

    def login(self, payload: UserLogin):
        user_record = self.user_repo.get_user_by_username(payload.username)
        if not user_record or not verify_password(payload.password, user_record["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        token = create_access_token({"user_id": user_record["id"]})
        return token
