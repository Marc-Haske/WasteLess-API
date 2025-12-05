from datetime import timedelta
import pytest
from jose import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from old_main import (
    normalize_name,
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
)


def test_normalize_name_trims_and_lowercases():
    assert normalize_name("  ApFel  ") == "apfel"
    assert normalize_name("\tBrot\n") == "brot"
    assert normalize_name("  KäSe") == "käse"


def test_hash_and_verify_password():
    plain = "mein-geheimes-passwort"
    hashed = hash_password(plain)

    assert hashed != plain  # darf nicht im Klartext sein
    assert verify_password(plain, hashed) is True
    assert verify_password("falsches-passwort", hashed) is False


def test_create_access_token_contains_user_id_and_exp():
    data = {"user_id": 123}
    token = create_access_token(data)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["user_id"] == 123
    assert "exp" in decoded


def test_create_access_token_with_custom_expiry():
    data = {"user_id": 1}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["user_id"] == 1
    assert "exp" in decoded


def test_get_current_user_valid_token():
    # Gültigen Token erzeugen
    token = create_access_token({"user_id": 42})
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    user_id = get_current_user(credentials)
    assert user_id == 42


def test_get_current_user_invalid_token_raises_http_exception():
    # Ungültiger Token (z. B. Müll)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.value")

    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials)

    assert exc.value.status_code == 401
