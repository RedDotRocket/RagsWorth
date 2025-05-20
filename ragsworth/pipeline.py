"""
Core pipeline interfaces and base classes for the RagsWorth processing stages.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class Document:
    """Represents a document or text chunk with its metadata."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    score: Optional[float] = None

@dataclass
class ChatRequest:
    """Represents an incoming chat request."""
    session_id: str
    user_message: str
    metadata: Dict[str, Any]

@dataclass
class ChatResponse:
    """Represents the response to a chat request."""
    session_id: str
    bot_reply: str
    source_documents: List[Document]
    metadata: Dict[str, Any]

class PipelineStage(ABC):
    """Base class for all pipeline stages."""

    @abstractmethod
    async def process(self, request: ChatRequest, context: Dict[str, Any]) -> ChatRequest:
        """Process the request and update the context."""
        pass

class Pipeline:
    """Main pipeline that orchestrates the processing stages."""

    def __init__(self, stages: List[PipelineStage]):
        self.stages = stages

    async def process(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request through all pipeline stages."""
        context: Dict[str, Any] = {}

        # Process through all stages
        for stage in self.stages:
            request = await stage.process(request, context)

        # Construct response from context
        return ChatResponse(
            session_id=request.session_id,
            bot_reply=context.get("bot_reply", ""),
            source_documents=context.get("source_documents", []),
            metadata=context.get("metadata", {})
        )