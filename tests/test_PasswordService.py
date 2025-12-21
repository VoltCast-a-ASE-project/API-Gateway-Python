from app.PasswordService import PasswordService

def test_create_password_hash_returns_string():
    password = "geheim123"
    hashed = PasswordService.create_password_hash(password)

    assert isinstance(hashed, str)
    assert hashed != password

def test_verify_password_correct_password():
    password = "geheim123"
    hashed = PasswordService.create_password_hash(password)

    assert PasswordService.verify_password(password, hashed) is True

def test_verify_password_wrong_password():
    password = "geheim123"
    hashed = PasswordService.create_password_hash(password)

    assert PasswordService.verify_password("falsch", hashed) is False
    