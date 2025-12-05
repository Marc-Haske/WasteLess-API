from supabase import Client
from app.models.schemas import RecipeCreate
from app.services.utils import normalize_name

class RecipeRepository:
    def __init__(self, client: Client):
        self.client = client

    def create_recipe(self, user_id: int, payload: RecipeCreate):
        recipe_resp = (
            self.client.table("recipes")
            .insert({
                "user_id": user_id,
                "title": payload.title,
                "description": payload.description or "",
            })
            .execute()
        )
        return recipe_resp.data[0] if recipe_resp.data else None

    def add_ingredients(self, recipe_id: int, ingredients: list):
        ing_rows = [
            {
                "recipe_id": recipe_id,
                "name": ing.name,
                "name_norm": normalize_name(ing.name),
                "quantity": ing.quantity,
                "unit": ing.unit,
            }
            for ing in ingredients
        ]
        resp = self.client.table("recipe_ingredients").insert(ing_rows).execute()
        return resp.data

    def get_recipes_for_user(self, user_id: int):
        resp = self.client.table("recipes").select("*").eq("user_id", user_id).execute()
        return resp.data or []

    def get_ingredients_for_recipe(self, recipe_id: int):
        resp = (
            self.client.table("recipe_ingredients")
            .select("*")
            .eq("recipe_id", recipe_id)
            .execute()
        )
        return resp.data or []
