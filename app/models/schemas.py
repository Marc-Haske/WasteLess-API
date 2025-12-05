from datetime import date
from typing import Optional, List
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class FoodItemCreate(BaseModel):
    name: str
    quantity: float
    unit: str
    expiration_date: date

class FoodItemConsume(BaseModel):
    quantity: float

class RecipeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    ingredients: List[FoodItemCreate]
