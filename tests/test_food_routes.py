from datetime import date


def test_list_food_items_forbidden_for_other_user(client):
    """
    current_user_id wird im conftest.py auf 1 gesetzt.
    Wir rufen hier /users/2/food auf => sollte 403 sein.
    """
    response = client.get("/users/2/food")
    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"


def test_list_food_items_returns_items(client, monkeypatch):
    class FakeResponse:
        def __init__(self, data):
            self.data = data

    def fake_get_all_food_items(user_id: int):
        assert user_id == 1
        return FakeResponse(
            data=[
                {
                    "id": 10,
                    "user_id": 1,
                    "name": "Milch",
                    "name_norm": "milch",
                    "quantity": 1.0,
                    "unit": "l",
                    "expiration_date": str(date(2025, 12, 1)),
                }
            ]
        )

    monkeypatch.setattr("main.get_all_food_items", fake_get_all_food_items)

    response = client.get("/users/1/food")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == "Milch"


def test_add_food_item_success(client, monkeypatch):
    class FakeResponse:
        def __init__(self, data):
            self.data = data

    def fake_add_or_update_food_item(user_id, item):
        assert user_id == 1
        # Wir tun so, als wäre ein neues Item angelegt worden
        return FakeResponse(
            data=[
                {
                    "id": 42,
                    "user_id": user_id,
                    "name": item.name,
                    "name_norm": item.name.lower(),
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "expiration_date": str(item.expiration_date),
                }
            ]
        ), "created"

    monkeypatch.setattr("main.add_or_update_food_item", fake_add_or_update_food_item)

    payload = {
        "name": "Milch",
        "quantity": 2,
        "unit": "l",
        "expiration_date": "2025-12-01",
    }

    response = client.post("/users/1/food", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Item created"
    assert body["data"][0]["name"] == "Milch"


def test_food_item_detail_not_found_returns_404(client, monkeypatch):
    def fake_get_food_item_detail(user_id: int, item_id: int):
        return None  # Item existiert nicht

    monkeypatch.setattr("main.get_food_item_detail", fake_get_food_item_detail)

    response = client.get("/users/1/food/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"
