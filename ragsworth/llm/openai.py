"""
OpenAI LLM client implementation.
"""

import os
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from .base import LLMClient, LLMConfig, LLMResponse

class OpenAIClient(LLMClient):
    """OpenAI API client implementation."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Validate model name
        if not config.model.startswith(("gpt-3.5", "gpt-4")):
            raise ValueError(f"Unsupported OpenAI model: {config.model}")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None
    ) -> LLMResponse:
        """Generate a response using OpenAI's chat completion API."""

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

        # Call OpenAI API
        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            top_p=self.config.top_p,
            frequency_penalty=self.config.frequency_penalty,
            presence_penalty=self.config.presence_penalty,
            stop=self.config.stop_sequences,
            **self.config.extra_params or {}
        )

        # Extract response
        choice = response.choices[0]
        return LLMResponse(
            text=choice.message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=choice.finish_reason,
            metadata={"response_id": response.id}
        )

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI's embedding API."""

        # Call OpenAI API
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )

        # Extract embeddings
        return [data.embedding for data in response.data]