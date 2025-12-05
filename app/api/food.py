from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user_id
from app.models.schemas import FoodItemCreate, FoodItemConsume
from app.api.deps import get_food_service
from app.services.food_service import FoodService

router = APIRouter(tags=["food"])

def assert_owner(current_user_id: int, user_id: int):
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

@router.post("/users/{user_id}/food")
def add_food_item(
    user_id: int,
    item: FoodItemCreate,
    service: FoodService = Depends(get_food_service),
    current_user_id: int = Depends(get_current_user_id),
):
    assert_owner(current_user_id, user_id)
    status, data = service.add_or_update_food_item(user_id, item)
    return {"message": f"Item {status}", "data": data}

@router.get("/users/{user_id}/food")
def list_food_items(
    user_id: int,
    service: FoodService = Depends(get_food_service),
    current_user_id: int = Depends(get_current_user_id),
):
    assert_owner(current_user_id, user_id)
    items = service.list_food_items(user_id)
    return {"items": items}

@router.get("/users/{user_id}/food/{item_id}")
def food_item_detail(
    user_id: int,
    item_id: int,
    service: FoodService = Depends(get_food_service),
    current_user_id: int = Depends(get_current_user_id),
):
    assert_owner(current_user_id, user_id)
    return service.get_food_item(user_id, item_id)

@router.post("/users/{user_id}/food/{item_id}/consume")
def consume_item(
    user_id: int,
    item_id: int,
    body: FoodItemConsume,
    service: FoodService = Depends(get_food_service),
    current_user_id: int = Depends(get_current_user_id),
):
    assert_owner(current_user_id, user_id)
    return service.consume_item(user_id, item_id, body)

@router.delete("/users/{user_id}/food/{item_id}")
def delete_item(
    user_id: int,
    item_id: int,
    service: FoodService = Depends(get_food_service),
    current_user_id: int = Depends(get_current_user_id),
):
    assert_owner(current_user_id, user_id)
    return service.delete_item(user_id, item_id)

@router.delete("/users/{user_id}/food")
def delete_user_food(
    user_id: int,
    service: FoodService = Depends(get_food_service),
    current_user_id: int = Depends(get_current_user_id),
):
    assert_owner(current_user_id, user_id)
    return service.delete_all_food(user_id)

@router.get("/users/{user_id}/food/expiring")
def expiring_items(
    user_id: int,
    days: int = 5,
    service: FoodService = Depends(get_food_service),
    current_user_id: int = Depends(get_current_user_id),
):
    assert_owner(current_user_id, user_id)
    return service.get_expiring_items(user_id, days)
