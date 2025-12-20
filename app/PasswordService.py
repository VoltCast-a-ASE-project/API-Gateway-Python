from pwdlib import PasswordHash
class PasswordService:

    @staticmethod
    def create_password_hash(password: str) -> str:
        password_hash = PasswordHash.recommended()
        return password_hash.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        password_hash = PasswordHash.recommended()
        return password_hash.verify(plain_password, hashed_password)
