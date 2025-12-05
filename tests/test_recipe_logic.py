from datetime import date

import types

from old_main import compute_recipe_suggestions


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeTable:
    """
    Sehr einfache Fake-Table-Implementierung, die nur das unterstützt,
    was compute_recipe_suggestions nutzt (select, eq, execute).
    """

    def __init__(self, rows):
        self._rows = rows
        self._filters = {}

    def select(self, *args, **kwargs):
        return self

    def eq(self, column, value):
        self._filters[column] = value
        return self

    def execute(self):
        filtered = [
            row
            for row in self._rows
            if all(row.get(col) == val for col, val in self._filters.items())
        ]
        return FakeResponse(filtered)


class FakeSupabase:
    def __init__(self, recipes, ingredients):
        self._recipes_table = FakeTable(recipes)
        self._ingredients_table = FakeTable(ingredients)

    def table(self, name: str):
        if name == "recipes":
            return self._recipes_table
        if name == "recipe_ingredients":
            return self._ingredients_table
        raise ValueError(f"Unknown table: {name}")


def test_compute_recipe_suggestions_user_can_make_recipe(monkeypatch):
    """
    Szenario:
      - User hat 'Tomate' im Stock
      - Es gibt ein Rezept 'Tomatensalat' mit Zutat 'Tomate'
      => compute_recipe_suggestions soll das Rezept ohne missing_ingredients vorschlagen.
    """

    # Fake get_all_food_items(user_id)
    def fake_get_all_food_items(user_id: int):
        assert user_id == 1
        return FakeResponse(
            data=[
                {
                    "id": 1,
                    "user_id": 1,
                    "name": "Tomate",
                    "name_norm": "tomate",
                    "quantity": 3,
                    "unit": "stk",
                    "expiration_date": str(date.today()),
                }
            ]
        )

    # Fake-Supabase mit einem Rezept + einer Zutat
    fake_supabase = FakeSupabase(
        recipes=[
            {"id": 100, "user_id": 1, "title": "Tomatensalat", "description": "Lecker."},
        ],
        ingredients=[
            {
                "id": 200,
                "recipe_id": 100,
                "name": "Tomate",
                "name_norm": "tomate",
                "quantity": 2,
                "unit": "stk",
            }
        ],
    )

    # main.get_all_food_items und main.supabase ersetzen
    monkeypatch.setattr("main.get_all_food_items", fake_get_all_food_items)
    monkeypatch.setattr("main.supabase", fake_supabase)

    from old_main import compute_recipe_suggestions  # nach Monkeypatch importieren (optional)

    result = compute_recipe_suggestions(user_id=1)
    suggestions = result.get("suggestions", [])

    # In deiner Implementierung liefert compute_recipe_suggestions ein Dict:
    # { "suggestions": [ {...}, {...} ] }
    assert isinstance(suggestions, list)
    assert len(suggestions) == 1
    recipe = suggestions[0]
    assert recipe["title"] == "Tomatensalat"
    assert "ingredients" in recipe
    assert recipe["ingredients"] == ["Tomate"]
