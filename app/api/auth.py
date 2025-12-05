from fastapi import APIRouter, Depends
from app.models.schemas import UserCreate, UserLogin
from app.api.deps import get_user_service
from app.services.user_service import UserService

router = APIRouter(tags=["auth"])

@router.post("/users/")
def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    data = service.create_user(user)
    return {"message": "User created", "data": data}

@router.post("/login/")
def login_user(payload: UserLogin, service: UserService = Depends(get_user_service)):
    token = service.login(payload)
    return {"access_token": token, "token_type": "bearer"}
