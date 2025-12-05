from datetime import date, timedelta
from fastapi import HTTPException

from app.models.schemas import FoodItemCreate, FoodItemConsume
from app.repositories.food import FoodRepository

class FoodService:
    def __init__(self, food_repo: FoodRepository):
        self.food_repo = food_repo

    def add_or_update_food_item(self, user_id: int, item: FoodItemCreate):
        existing = self.food_repo.find_existing_food_row(
            user_id=user_id,
            name=item.name,
            unit=item.unit,
            expiration_date=item.expiration_date,
        )
        if existing:
            new_qty = float(existing["quantity"]) + float(item.quantity)
            data = self.food_repo.update_food_quantity(existing["id"], user_id, new_qty)
            return "updated", data
        else:
            data = self.food_repo.insert_food_item(user_id, item)
            return "created", data

    def list_food_items(self, user_id: int):
        return self.food_repo.get_all_food_items(user_id)

    def get_food_item(self, user_id: int, item_id: int):
        item = self.food_repo.get_food_item_detail(user_id, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    def consume_item(self, user_id: int, item_id: int, body: FoodItemConsume):
        item = self.food_repo.get_food_item_detail(user_id, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        new_qty = float(item["quantity"]) - float(body.quantity)
        if new_qty <= 0:
            self.food_repo.delete_food_item(user_id, item_id)
            return {"message": "Item consumed and removed"}
        else:
            data = self.food_repo.update_food_quantity(item_id, user_id, new_qty)
            return {"message": "Item quantity updated", "data": data}

    def delete_item(self, user_id: int, item_id: int):
        self.food_repo.delete_food_item(user_id, item_id)
        return {"message": "Item deleted"}

    def delete_all_food(self, user_id: int):
        self.food_repo.delete_all_food_for_user(user_id)
        return {"message": f"All food items for user {user_id} deleted."}

    def get_expiring_items(self, user_id: int, days: int = 5):
        today = date.today()
        until = today + timedelta(days=days)
        items = self.food_repo.get_expiring_items(user_id, today, until)
        return {"items": items}
