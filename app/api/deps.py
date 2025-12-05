from fastapi import Depends
from app.db.supabase import get_supabase_client
from app.repositories.users import UserRepository
from app.repositories.food import FoodRepository
from app.repositories.recipes import RecipeRepository
from app.services.user_service import UserService
from app.services.food_service import FoodService
from app.services.recipe_service import RecipeService

def get_user_repo(client = Depends(get_supabase_client)):
    return UserRepository(client)

def get_food_repo(client = Depends(get_supabase_client)):
    return FoodRepository(client)

def get_recipe_repo(client = Depends(get_supabase_client)):
    return RecipeRepository(client)

def get_user_service(repo: UserRepository = Depends(get_user_repo)):
    return UserService(repo)

def get_food_service(repo: FoodRepository = Depends(get_food_repo)):
    return FoodService(repo)

def get_recipe_service(
    recipe_repo: RecipeRepository = Depends(get_recipe_repo),
    food_repo: FoodRepository = Depends(get_food_repo),
):
    return RecipeService(recipe_repo, food_repo)
