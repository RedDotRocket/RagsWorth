from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ChatRequestModel(BaseModel):
    """Chat request model."""
    session_id: str = Field(..., description="Unique session identifier")
    user_message: str = Field(..., description="User's message")
    context: Optional[List[Dict[str, str]]] = Field(None, description="Optional conversation context")

class DocumentModel(BaseModel):
    """Document model for responses."""
    id: str
    score: float
    snippet: str

class ChatResponseModel(BaseModel):
    """Chat response model."""
    session_id: str
    bot_reply: str
    source_documents: List[DocumentModel]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None 