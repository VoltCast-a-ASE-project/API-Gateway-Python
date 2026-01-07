from pwdlib import PasswordHash
class PasswordService:
    """
    Class holds method to create password hash and password validation.
    """

    @staticmethod
    def create_password_hash(password: str) -> str:
        """
        Method creates hash of passed password.
        :param password: Password string.
        :return: Hashed password
        """
        password_hash = PasswordHash.recommended()
        return password_hash.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Method checks hashed password from database and passed password from login request.
        :param plain_password: Password from login request.
        :param hashed_password: Password hash from database.
        :return: Boolean
        """
        password_hash = PasswordHash.recommended()
        return password_hash.verify(plain_password, hashed_password)
