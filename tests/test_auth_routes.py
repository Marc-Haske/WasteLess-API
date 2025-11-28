from datetime import datetime
import pytest

from main import app


def test_create_user_conflict_when_username_exists(client, monkeypatch):
    # Fake get_user_by_username -> tut so, als gäbe es den User schon
    def fake_get_user_by_username(username: str):
        return {"id": 1, "username": username}

    monkeypatch.setattr("main.get_user_by_username", fake_get_user_by_username)

    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret",
    }

    response = client.post("/users/", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Username already exists"


def test_create_user_success(client, monkeypatch):
    # Keine Kollision beim Usernamen
    def fake_get_user_by_username(username: str):
        return None

    class FakeResponse:
        def __init__(self, data):
            self.data = data

    def fake_create_user_in_db(user):
        # Einfach so tun, als wäre ein Datensatz in der DB angelegt worden
        return FakeResponse(
            data=[
                {
                    "id": 1,
                    "username": user.username,
                    "email": user.email,
                    "created_at": datetime.utcnow().isoformat(),
                }
            ]
        )

    monkeypatch.setattr("main.get_user_by_username", fake_get_user_by_username)
    monkeypatch.setattr("main.create_user_in_db", fake_create_user_in_db)

    payload = {
        "username": "bob",
        "email": "bob@example.com",
        "password": "pw",
    }

    response = client.post("/users/", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "User created"
    assert body["data"][0]["username"] == "bob"


def test_login_user_success(client, monkeypatch):
    # Fake User in "DB"
    fake_user = {
        "id": 1,
        "username": "alice",
        "password_hash": "hashed-password",
    }

    def fake_get_user_by_username(username: str):
        assert username == "alice"
        return fake_user

    def fake_verify_password(plain_password: str, hashed_password: str) -> bool:
        # Einfach: nur wenn genau diese Werte
        return plain_password == "secret" and hashed_password == fake_user["password_hash"]

    def fake_create_access_token(data: dict, expires_delta=None) -> str:
        # Token muss nur irgendein String sein
        return "fake.jwt.token"

    monkeypatch.setattr("main.get_user_by_username", fake_get_user_by_username)
    monkeypatch.setattr("main.verify_password", fake_verify_password)
    monkeypatch.setattr("main.create_access_token", fake_create_access_token)

    payload = {"username": "alice", "password": "secret"}
    response = client.post("/login/", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "fake.jwt.token"
    assert body["token_type"] == "bearer"


def test_login_user_invalid_credentials(client, monkeypatch):
    # Kein User gefunden
    def fake_get_user_by_username(username: str):
        return None

    monkeypatch.setattr("main.get_user_by_username", fake_get_user_by_username)

    payload = {"username": "alice", "password": "wrong"}
    response = client.post("/login/", json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"
