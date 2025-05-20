"""
Anthropic LLM client implementation.
"""

import os
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic

from .base import LLMClient, LLMConfig, LLMResponse

class AnthropicClient(LLMClient):
    """Anthropic API client implementation."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Validate model name
        if not config.model.startswith("claude-"):
            raise ValueError(f"Unsupported Anthropic model: {config.model}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None
    ) -> LLMResponse:
        """Generate a response using Anthropic's completion API."""
        
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
        
        # Call Anthropic API
        response = await self.client.messages.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            top_p=self.config.top_p,
            **self.config.extra_params or {}
        )
        
        return LLMResponse(
            text=response.content[0].text,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            finish_reason=response.stop_reason,
            metadata={"response": response.model_dump()}
        )
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Anthropic's embedding API.
        
        Note: Currently, Anthropic doesn't provide a public embeddings API.
        This method falls back to using their text completion API to generate
        a semantic representation of the text.
        """
        raise NotImplementedError(
            "Anthropic does not currently provide a public embeddings API. "
            "Please use OpenAI or Ollama for embeddings generation."
        ) 