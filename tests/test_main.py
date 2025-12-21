import pytest
from fastapi.testclient import TestClient

import app.main as main_module


# ---------- TestClient ----------
@pytest.fixture()
def client():
    return TestClient(main_module.app)


# ---------- Dummy DB ----------
class DummyDB:
    def setup_db(self):
        # DB setup not tested
        pass

    def write_user_data(self, user):
        return True

    def get_user_password(self, username):
        return [["hashed_pw"]]

    def write_microservice_data(self, body):
        return True


def test_register_success(client, monkeypatch):
    monkeypatch.setattr(main_module, "db", DummyDB())
    monkeypatch.setattr(main_module.PasswordService, "create_password_hash", lambda pw: "hashed_pw")
    monkeypatch.setattr(main_module.JwtService, "create_jwt", lambda username: "jwt_token")

    res = client.post(
        "/api/v1/auth/register",
        json={"email": "test@test.com", "password": "pw"},
    )

    assert res.status_code == 200
    assert res.json()["data"]["token"] == "jwt_token"


def test_register_conflict_email_in_use(client, monkeypatch):
    db = DummyDB()
    db.write_user_data = lambda user: False
    monkeypatch.setattr(main_module, "db", db)

    monkeypatch.setattr(main_module.PasswordService, "create_password_hash", lambda pw: "hashed_pw")

    res = client.post(
        "/api/v1/auth/register",
        json={"email": "test@test.com", "password": "pw"},
    )

    assert res.status_code == 409


def test_login_success(client, monkeypatch):
    monkeypatch.setattr(main_module, "db", DummyDB())
    monkeypatch.setattr(main_module.PasswordService, "verify_password", lambda p, h: True)
    monkeypatch.setattr(main_module.JwtService, "create_jwt", lambda u: "jwt_token")

    res = client.post(
        "/api/v1/auth/login",
        json={"email": "test@test.com", "password": "pw"},
    )

    assert res.status_code == 200
    assert res.json()["data"]["token"] == "jwt_token"


def test_login_wrong_credentials(client, monkeypatch):
    monkeypatch.setattr(main_module, "db", DummyDB())
    monkeypatch.setattr(main_module.PasswordService, "verify_password", lambda p, h: False)

    res = client.post(
        "/api/v1/auth/login",
        json={"email": "test@test.com", "password": "wrong"},
    )

    assert res.status_code == 401


def test_login_user_not_found(client, monkeypatch):
    db = DummyDB()
    db.get_user_password = lambda username: []
    monkeypatch.setattr(main_module, "db", db)

    res = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@test.com", "password": "pw"},
    )

    assert res.status_code in (401, 404, 500)


def test_excluded_routes_no_jwt_required(client, monkeypatch):
    monkeypatch.setattr(main_module, "db", DummyDB())
    monkeypatch.setattr(main_module.PasswordService, "create_password_hash", lambda pw: "hashed_pw")
    monkeypatch.setattr(main_module.JwtService, "create_jwt", lambda u: "jwt_token")

    res = client.post(
        "/api/v1/auth/register",
        json={"email": "test@test.com", "password": "pw"},
    )

    assert res.status_code == 200


def test_missing_authorization_header(client, monkeypatch):
    monkeypatch.setattr(main_module.JwtService, "verify_jwt", lambda t: True)

    res = client.get("/api/v1/shelly/test")

    assert res.status_code == 400


def test_invalid_token(client, monkeypatch):
    monkeypatch.setattr(main_module.JwtService, "verify_jwt", lambda t: False)

    res = client.get(
        "/api/v1/shelly/test",
        headers={"Authorization": "Bearer invalid"},
    )

    assert res.status_code == 401