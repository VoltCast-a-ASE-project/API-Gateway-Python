from app.PasswordService import PasswordService

def test_create_password_hash_returns_string():
    """
    Test password creation method.
    :return: None
    """
    password = "blabla"
    hashed = PasswordService.create_password_hash(password)

    assert isinstance(hashed, str)
    assert hashed != password

def test_verify_password_correct_password():
    """
    Test method that verifies passed password with password hash from database.
    :return: None
    """
    password = "blabla"
    hashed = PasswordService.create_password_hash(password)

    assert PasswordService.verify_password(password, hashed) is True

def test_verify_password_wrong_password():
    """
    Test method that verifies passed password with wrong password.
    :return: None
    """
    password = "blabla"
    hashed = PasswordService.create_password_hash(password)

    assert PasswordService.verify_password("blablalba", hashed) is False
    