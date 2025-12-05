from datetime import date
from supabase import Client
from app.models.schemas import FoodItemCreate
from app.services.utils import normalize_name

class FoodRepository:
    def __init__(self, client: Client):
        self.client = client

    def find_existing_food_row(self, user_id: int, name: str, unit: str, expiration_date: date):
        resp = (
            self.client.table("food_stock")
            .select("*")
            .eq("user_id", user_id)
            .eq("name_norm", normalize_name(name))
            .eq("unit", unit)
            .eq("expiration_date", str(expiration_date))
            .limit(1)
            .execute()
        )
        return resp.data[0] if resp.data else None

    def insert_food_item(self, user_id: int, item: FoodItemCreate):
        resp = (
            self.client.table("food_stock")
            .insert({
                "user_id": user_id,
                "name": item.name,
                "name_norm": normalize_name(item.name),
                "quantity": item.quantity,
                "unit": item.unit,
                "expiration_date": str(item.expiration_date),
            })
            .execute()
        )
        return resp.data

    def update_food_quantity(self, food_id: int, user_id: int, quantity: float):
        resp = (
            self.client.table("food_stock")
            .update({"quantity": quantity})
            .eq("id", food_id)
            .eq("user_id", user_id)
            .execute()
        )
        return resp.data

    def get_all_food_items(self, user_id: int):
        resp = self.client.table("food_stock").select("*").eq("user_id", user_id).execute()
        return resp.data or []

    def get_food_item_detail(self, user_id: int, item_id: int):
        resp = (
            self.client.table("food_stock")
            .select("*")
            .eq("user_id", user_id)
            .eq("id", item_id)
            .limit(1)
            .execute()
        )
        return resp.data[0] if resp.data else None

    def delete_food_item(self, user_id: int, item_id: int):
        self.client.table("food_stock").delete().eq("user_id", user_id).eq("id", item_id).execute()

    def delete_all_food_for_user(self, user_id: int):
        self.client.table("food_stock").delete().eq("user_id", user_id).execute()

    def get_expiring_items(self, user_id: int, start: date, end: date):
        resp = (
            self.client.table("food_stock")
            .select("*")
            .eq("user_id", user_id)
            .gte("expiration_date", str(start))
            .lte("expiration_date", str(end))
            .order("expiration_date", desc=False)
            .execute()
        )
        return resp.data or []
