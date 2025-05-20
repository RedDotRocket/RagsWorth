from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Dict, Any
import jwt as pyjwt
from datetime import timezone

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "a0fe115a478849b00ad65bb02816127c6e94a53babaa25e2cd48aa479a575bf7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Argon2PHasher:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2.

        Args:
            password: The plaintext password as a string

        Returns:
            A string containing the hashed password

        Raises:
            ValueError: If the password is None or empty
        """
        # Validate password
        if password is None or password == "":
            raise ValueError("Password cannot be None or empty")

        # Ensure password is in bytes if it's a string
        if isinstance(password, str):
            password_bytes = password.encode('utf-8')
        else:
            password_bytes = password

        # Hash the password
        return self.pwd_context.hash(password_bytes)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash.

        Args:
            plain_password: The plaintext password to verify
            hashed_password: The hashed password to verify against

        Returns:
            True if the password matches, False otherwise
        """
        # Ensure password is in bytes if it's a string
        if isinstance(plain_password, str):
            plain_password_bytes = plain_password.encode('utf-8')
        else:
            plain_password_bytes = plain_password

        return self.pwd_context.verify(plain_password_bytes, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except pyjwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except pyjwt.InvalidTokenError:
        raise Exception("Invalid token")
    except Exception as e:
        raise Exception(f"An error occurred while decoding the token: {str(e)}")
    return payload