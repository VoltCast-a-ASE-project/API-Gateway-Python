import datetime
import os
import jwt

from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv



class JwtService:
    """
    Class holds methods for JSON Web Token creation and validation.
    """

    @staticmethod
    def create_jwt(username):
        """
        Method creates a user specific JSON Web Token and returns it.
        :param username: Username as string
        :return: JWT as string
        """
        load_dotenv()
        secret = os.getenv("JWT_SECRET")
        algorithm = os.getenv("ALGORITHM")
        access_token_expire_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
        expires = datetime.now(timezone.utc) + timedelta(minutes=int(access_token_expire_minutes))

        to_encode = {
            "sub": username,
            "exp": expires
        }

        return jwt.encode(to_encode, secret, algorithm=algorithm)


    @staticmethod
    def verify_jwt(token) -> bool:
        """
        Method validates passed JSON Web Token. Returns boolean true or false
        """
        load_dotenv()
        secret = os.getenv("JWT_SECRET")
        algorithm = os.getenv("ALGORITHM")
        try:
            jwt.decode(token, key=secret, algorithms=[algorithm,])
        except Exception:
            return False

        return True

