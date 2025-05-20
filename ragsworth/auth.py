from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
import jwt as pyjwt
from datetime import timezone

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "a0fe115a478849b00ad65bb02816127c6e94a53babaa25e2cd48aa479a575bf7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

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

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a new access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        str: The encoded JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a new refresh token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        str: The encoded JWT refresh token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_token_pair(data: dict) -> Tuple[str, str]:
    """Create both access and refresh tokens.
    
    Args:
        data: The data to encode in the tokens
        
    Returns:
        Tuple[str, str]: A tuple containing (access_token, refresh_token)
    """
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    return access_token, refresh_token

def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate an access token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        Dict[str, Any]: The decoded token payload
        
    Raises:
        Exception: If the token is invalid, expired, or not an access token
    """
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise Exception("Invalid token type: expected access token")
        return payload
    except pyjwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except pyjwt.InvalidTokenError:
        raise Exception("Invalid token")
    except Exception as e:
        raise Exception(f"An error occurred while decoding the token: {str(e)}")

def decode_refresh_token(token: str) -> Dict[str, Any]:
    """Decode and validate a refresh token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        Dict[str, Any]: The decoded token payload
        
    Raises:
        Exception: If the token is invalid, expired, or not a refresh token
    """
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise Exception("Invalid token type: expected refresh token")
        return payload
    except pyjwt.ExpiredSignatureError:
        raise Exception("Refresh token has expired")
    except pyjwt.InvalidTokenError:
        raise Exception("Invalid refresh token")
    except Exception as e:
        raise Exception(f"An error occurred while decoding the refresh token: {str(e)}")

def refresh_access_token(refresh_token: str) -> str:
    """Create a new access token using a valid refresh token.
    
    Args:
        refresh_token: The refresh token to use
        
    Returns:
        str: A new access token
        
    Raises:
        Exception: If the refresh token is invalid or expired
    """
    try:
        payload = decode_refresh_token(refresh_token)
        # Remove token type and expiration from payload
        payload.pop("type", None)
        payload.pop("exp", None)
        # Create new access token
        return create_access_token(payload)
    except Exception as e:
        raise Exception(f"Failed to refresh access token: {str(e)}")