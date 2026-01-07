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
    """
    Test creation of database.
    :param db_instance: Mocking instance of database.
    :return: None
    """
    con = db_instance.establish_con()
    cur = con.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
    assert cur.fetchone() is not None

    con.close()


def test_write_user_data_success(db_instance):
    """
    Test write user data to database.
    :param db_instance: Mocking instance of database.
    :return: None
    """
    u = DummyUser("a@b.com", "hashed")
    assert db_instance.write_user_data(u) is True

    res = db_instance.get_user_password("a@b.com")
    assert res == [("hashed",)]


def test_write_user_data_duplicate_username_returns_false(db_instance):
    """
    Test to write two times same username to database.
    Mocking instance of database.
    :return: None
    """
    u1 = DummyUser("dup@b.com", "hashed1")
    assert db_instance.write_user_data(u1) is True

    u2 = DummyUser("dup@b.com", "hashed2")
    assert db_instance.write_user_data(u2) is False


def test_get_user_password_unknown_user_returns_empty_list(db_instance):
    """
    Test to return no password for unexistant user.
    :param db_instance: Mocking instance of database.
    :return: None
    """
    res = db_instance.get_user_password("missing@b.com")
    assert res == []
