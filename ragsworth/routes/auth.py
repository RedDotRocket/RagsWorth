from typing import List, Annotated
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..models.api import Token
from ..models.users import User
from ..auth import Argon2PHasher, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, decode_access_token
from ..db.engine import Database
from ..config.logging_config import get_logger

logger = get_logger("routes.auth")

router = APIRouter(tags=["authentication"])

def get_current_user_dependency(oauth2_scheme, db: Database):
    """Create a dependency for getting the current user from the token."""
    
    async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
        """Get the current user from the token."""
        try:
            # Decode the token
            payload = decode_access_token(token)
            username = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Get the user from the database
            user = db.get_user_by_username(username)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return user
        except Exception as e:
            logger.error(f"Auth error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    return get_current_user

def create_auth_router(db: Database):
    """Create the authentication router with dependencies injected."""
    
    @router.post("/token", response_model=Token)
    async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> Token:
        """Generate JWT token for authenticated user."""
        try:
            # Debug info
            logger.info(f"Login attempt for user: {form_data.username}")

            # Get user by username
            user = db.get_user_by_username(form_data.username)
            if not user:
                logger.warning(f"User not found: {form_data.username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Verify password
            hasher = Argon2PHasher()
            if not hasher.verify_password(form_data.password, user.hashed_password):
                logger.warning(f"Password verification failed for user: {form_data.username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Generate token
            logger.debug(f"Generating token for user: {form_data.username}")
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
            )

            logger.info(f"Token generated successfully for user: {form_data.username}")
            return Token(access_token=access_token, token_type="bearer")
        except Exception as e:
            logger.error(f"Error in token endpoint: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating token: {str(e)}"
            )
    
    @router.post("/register", response_model=User, status_code=201)
    async def register_user(user: User) -> User:
        """Register a new user."""
        try:
            # Check if user already exists
            existing_user = db.get_user_by_username(user.username)
            if existing_user:
                raise HTTPException(
                    status_code=409,
                    detail=f"User with username '{user.username}' already exists"
                )

            # Check if email already exists
            existing_email = db.get_user_by_email(user.email)
            if existing_email:
                raise HTTPException(
                    status_code=409,
                    detail=f"User with email '{user.email}' already exists"
                )

            # Validate required fields
            if not user.username or not user.email or not user.password:
                raise HTTPException(
                    status_code=400,
                    detail="Username, email, and password are required"
                )

            # Hash the password
            hasher = Argon2PHasher()
            user.hashed_password = hasher.hash_password(user.password)

            # Store the user
            db.add_user(user)

            # Don't return the password in the response
            user.password = None
            return user
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            if "already exists" in str(e):
                raise HTTPException(status_code=409, detail=str(e))
            raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    
    return router 