import os
import time
import jwt
import pytest
from datetime import datetime, timedelta, timezone

from app.JwtService import JwtService


@pytest.fixture(autouse=True)
def jwt_env(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1")


def test_create_jwt_returns_string():
    token = JwtService.create_jwt("user@test.com")
    assert isinstance(token, str)
    assert token.count(".") == 2


def test_create_jwt_contains_correct_subject():
    token = JwtService.create_jwt("user@test.com")

    decoded = jwt.decode(
        token,
        key=os.getenv("JWT_SECRET"),
        algorithms=[os.getenv("ALGORITHM")],
    )

    assert decoded["sub"] == "user@test.com"


def test_create_jwt_has_expiration_in_future():
    token = JwtService.create_jwt("user@test.com")

    decoded = jwt.decode(
        token,
        key=os.getenv("JWT_SECRET"),
        algorithms=[os.getenv("ALGORITHM")],
    )

    exp = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
    assert exp > datetime.now(timezone.utc)


def test_verify_jwt_valid_token_returns_true():
    token = JwtService.create_jwt("user@test.com")
    assert JwtService.verify_jwt(token) is True


def test_verify_jwt_invalid_signature_returns_false():
    token = JwtService.create_jwt("user@test.com")

    parts = token.split(".")
    fake_token = parts[0] + "." + parts[1] + ".invalid"

    assert JwtService.verify_jwt(fake_token) is False


def test_verify_jwt_expired_token_returns_false(monkeypatch):
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "0")

    token = JwtService.create_jwt("user@test.com")

    time.sleep(1)

    assert JwtService.verify_jwt(token) is False


def test_verify_jwt_random_string_returns_false():
    assert JwtService.verify_jwt("this.is.not.a.jwt") is False
