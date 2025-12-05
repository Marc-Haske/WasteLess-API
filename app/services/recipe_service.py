from app.repositories.recipes import RecipeRepository
from app.repositories.food import FoodRepository
from app.models.schemas import RecipeCreate

class RecipeService:
    def __init__(self, recipe_repo: RecipeRepository, food_repo: FoodRepository):
        self.recipe_repo = recipe_repo
        self.food_repo = food_repo

    def save_recipe(self, user_id: int, payload: RecipeCreate):
        recipe = self.recipe_repo.create_recipe(user_id, payload)
        if not recipe:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Error creating recipe")

        ing_data = self.recipe_repo.add_ingredients(recipe["id"], payload.ingredients)
        return {"message": "Recipe saved", "recipe": recipe, "ingredients": ing_data}

    def compute_recipe_suggestions(self, user_id: int):
        user_food_items = {
            item["name_norm"]: item for item in self.food_repo.get_all_food_items(user_id)
        }

        recipes = self.recipe_repo.get_recipes_for_user(user_id)
        if not recipes:
            return {"suggestions": []}

        suggestions = []

        for recipe in recipes:
            ingredients = self.recipe_repo.get_ingredients_for_recipe(recipe["id"])
            if not ingredients:
                continue

            missing = []
            can_make = True

            for ing in ingredients:
                name_norm = ing["name_norm"]
                if name_norm not in user_food_items:
                    missing.append(ing["name"])
                    can_make = False

            if can_make:
                suggestions.append({
                    "title": recipe["title"],
                    "description": recipe["description"],
                    "ingredients": [i["name"] for i in ingredients],
                })
            elif missing:
                suggestions.append({
                    "title": recipe["title"],
                    "description": recipe["description"],
                    "missing_ingredients": missing,
                })

        return {"suggestions": suggestions}
