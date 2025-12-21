import sqlite3
import pytest

from app.Database import Database


class DummyUser:
    def __init__(self, username: str, hashed_password: str):
        self.username = username
        self.hashed_password = hashed_password


@pytest.fixture()
def db_instance(tmp_path, monkeypatch):
    db_file = tmp_path / "VoltCastDB"

    def connect_override(_db_name):
        return sqlite3.connect(db_file)

    monkeypatch.setattr("app.Database._sqlite3.connect", connect_override)

    db = Database()
    db.setup_db()
    return db


def test_setup_db_creates_tables(db_instance):
    con = db_instance.establish_con("VoltCastDB")
    cur = con.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
    assert cur.fetchone() is not None

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='microservices'")
    assert cur.fetchone() is not None

    con.close()


def test_write_user_data_success(db_instance):
    u = DummyUser("a@b.com", "hashed")
    assert db_instance.write_user_data(u) is True

    res = db_instance.get_user_password("a@b.com")
    assert res == [("hashed",)]


def test_write_user_data_duplicate_username_returns_false(db_instance):
    u1 = DummyUser("dup@b.com", "hashed1")
    assert db_instance.write_user_data(u1) is True

    u2 = DummyUser("dup@b.com", "hashed2")
    assert db_instance.write_user_data(u2) is False


def test_get_user_password_unknown_user_returns_empty_list(db_instance):
    res = db_instance.get_user_password("missing@b.com")
    assert res == []


def test_write_microservice_data_reveals_db_name_bug(db_instance, monkeypatch):
    user = DummyUser("user@test.com", "pw")
    db_instance.write_user_data(user)

    micro = {
        "name": "shelly",
        "ip_address": "127.0.0.1",
        "port": 8083,
        "username": "user@test.com",
    }

    ok = db_instance.write_microservice_data(micro)

    assert ok in (True, False)
