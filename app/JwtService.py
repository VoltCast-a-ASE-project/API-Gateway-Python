import os
import jwt

from dotenv import load_dotenv

class JwtService:

    @staticmethod
    def create_jwt(username):
        load_dotenv()
        secret = os.getenv("JWT_SECRET")
        algorithm = os.getenv("ALGORITHM")
        access_token_expire_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

        to_encode = {
            "sub": username,
            "exp": access_token_expire_minutes
        }

        return jwt.encode(to_encode, secret, algorithm=algorithm)



