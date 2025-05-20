"""
Ollama LLM client implementation.
"""

from typing import  Dict, List, Optional

import aiohttp

from .base import LLMClient, LLMConfig, LLMResponse
from ..config.logging_config import get_logger

logger = get_logger("llm.ollama")

class OllamaClient(LLMClient):
    """Ollama API client implementation."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = "http://localhost:11434"  # Default Ollama API endpoint

        # Get embedding model from config or fall back to main model
        self.embedding_model = (
            config.extra_params.get("embedding_model")
            if config.extra_params
            else config.model
        )

        # Set base URL if provided in extra_params
        if config.extra_params and "base_url" in config.extra_params:
            self.base_url = config.extra_params["base_url"]

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None
    ) -> LLMResponse:
        """Generate a response using Ollama's completion API."""

        # Build messages list
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add conversation context if provided
        if context:
            for turn in context:
                messages.append({
                    "role": turn.get("role", "user"),
                    "content": turn.get("content", "")
                })

        # Add current prompt
        messages.append({"role": "user", "content": prompt})

        # Prepare request payload
        logger.info(f"Using model: {self.config.model}")
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "frequency_penalty": self.config.frequency_penalty,
                "presence_penalty": self.config.presence_penalty
            }
        }

        if self.config.max_tokens:
            payload["options"]["num_predict"] = self.config.max_tokens

        # Add any extra parameters
        if self.config.extra_params:
            payload["options"].update(self.config.extra_params)

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/chat", json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {error_text}")

                data = await response.json()

        return LLMResponse(
            text=data["message"]["content"],
            model=self.config.model,
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("total_eval_count", 0)
            },
            finish_reason=data.get("done", True) and "stop" or "length",
            metadata={"response": data}
        )

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = []
        async with aiohttp.ClientSession() as session:
            for text in texts:
                payload = {
                    "model": self.embedding_model,
                    "prompt": text
                }

                async with session.post(f"{self.base_url}/api/embeddings", json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {error_text}")

                    data = await response.json()
                    embeddings.append(data["embedding"])

        return embeddings
