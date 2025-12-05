from fastapi import FastAPI
from app.api import auth
from app.api import recipes, food

app = FastAPI(title="WasteLess API")

app.include_router(auth.router)
app.include_router(food.router)
app.include_router(recipes.router)
