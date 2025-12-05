from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_recipe_service
from app.core.security import get_current_user_id
from app.models.schemas import RecipeCreate
from app.services.recipe_service import RecipeService

router = APIRouter(tags=["recipes"])

def assert_owner(current_user_id: int, user_id: int):
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

@router.get("/users/{user_id}/recipes/suggest")
def suggest_recipes(
    user_id: int,
    service: RecipeService = Depends(get_recipe_service),
    current_user_id: int = Depends(get_current_user_id),
):
    assert_owner(current_user_id, user_id)
    return service.compute_recipe_suggestions(user_id)

@router.post("/users/{user_id}/recipes")
def save_recipe(
    user_id: int,
    payload: RecipeCreate,
    service: RecipeService = Depends(get_recipe_service),
    current_user_id: int = Depends(get_current_user_id),
):
    assert_owner(current_user_id, user_id)
    return service.save_recipe(user_id, payload)
