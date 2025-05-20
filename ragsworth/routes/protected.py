from typing import Annotated
from fastapi import APIRouter, Depends

from ..models.users import User
from ..config.logging_config import get_logger

logger = get_logger("routes.protected")

router = APIRouter(prefix="/protected", tags=["protected"])

class ProtectedRouter:
    def __init__(self, vector_store=None):
        self.vector_store = vector_store

    def create_router(self, get_current_user):
        """Create a configured router with protected endpoints."""

        @router.get("/documents", response_model=dict)
        async def get_document_stats(current_user: Annotated[User, Depends(get_current_user)]):
            """Get document statistics (protected endpoint example)."""
            try:
                # Get document count - safely handle case where documents attribute might not exist
                doc_count = 0
                if self.vector_store:
                    if hasattr(self.vector_store, 'documents'):
                        doc_count = len(self.vector_store.documents)
                    else:
                        logger.warning("Vector store has no documents attribute")
                else:
                    logger.warning("Vector store not initialized")

                return {
                    "document_count": doc_count,
                    "user": current_user.username,
                    "message": "This is a protected endpoint that requires authentication"
                }
            except Exception as e:
                logger.error(f"Protected endpoint error: {str(e)}", exc_info=True)
                return {
                    "document_count": 0,
                    "user": current_user.username,
                    "message": "This is a protected endpoint that requires authentication",
                    "error": f"Could not retrieve document count: {str(e)}"
                }

        @router.get("/simple", response_model=dict)
        async def get_protected_simple(current_user: Annotated[User, Depends(get_current_user)]):
            """A simple protected endpoint that doesn't access any complex components."""
            return {
                "message": "You have accessed a protected endpoint",
                "username": current_user.username,
                "user_id": current_user.id,
                "protected": True
            }

        return router
