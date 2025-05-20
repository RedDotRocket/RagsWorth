from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException

from ..models.users import User
from ..db.engine import Database

router = APIRouter(tags=["users"])

def create_user_router(db: Database, get_current_user):
    """Create the user router with dependencies injected."""

    @router.get("/me", response_model=User)
    async def get_current_user_info(current_user: Annotated[User, Depends(get_current_user)]):
        """Get current authenticated user info."""
        return current_user

    @router.get("/get_user/{user_id}", response_model=User)
    async def get_user(user_id: int) -> User:
        """Get user by ID."""
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @router.get("/get_all_users", response_model=List[User])
    async def get_all_users() -> List[User]:
        """Get all users."""
        users = db.get_all_users()
        return users

    return router