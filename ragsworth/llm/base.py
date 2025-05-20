"""
Base interface for LLM clients.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class LLMConfig:
    """Configuration for LLM clients."""
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None
    extra_params: Dict[str, Any] = None

@dataclass
class LLMResponse:
    """Response from an LLM."""
    text: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    metadata: Dict[str, Any]

class LLMClient(ABC):
    """Base class for LLM clients."""

    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None
    ) -> LLMResponse:
        """Generate a response from the LLM.

        Args:
            prompt: The user's message or prompt
            system_prompt: Optional system prompt to guide the model's behavior
            context: Optional list of previous conversation turns

        Returns:
            LLMResponse containing the generated text and metadata
        """
        pass

    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        pass