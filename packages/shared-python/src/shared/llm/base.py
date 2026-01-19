"""Abstract LLM provider interface."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any, Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    """Standard response from LLM providers."""
    
    content: str
    model: str
    usage: Optional[dict] = None
    finish_reason: Optional[str] = None
    raw_response: Optional[dict] = None


class LLMProvider(ABC):
    """Abstract interface for all LLM providers.
    
    Implementations:
    - OpenAIProvider
    - AnthropicProvider
    - AzureOpenAIProvider
    - OllamaProvider
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the LLM provider."""
        ...

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a completion for the given prompt.
        
        Args:
            prompt: The user prompt/message
            system_prompt: Optional system instructions
            temperature: Sampling temperature (0.0 - 2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters
            
        Returns:
            LLMResponse with generated content
        """
        ...

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Stream a completion for the given prompt.
        
        Args:
            prompt: The user prompt/message
            system_prompt: Optional system instructions
            temperature: Sampling temperature (0.0 - 2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters
            
        Yields:
            String chunks as they are generated
        """
        ...

    @abstractmethod
    async def structured_output(
        self,
        prompt: str,
        schema: dict,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        **kwargs: Any,
    ) -> dict:
        """Generate structured output matching the given JSON schema.
        
        Args:
            prompt: The user prompt/message
            schema: JSON schema for the expected output
            system_prompt: Optional system instructions
            temperature: Sampling temperature (lower for more deterministic)
            **kwargs: Provider-specific parameters
            
        Returns:
            Parsed JSON object matching the schema
        """
        ...

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> LLMResponse:
        """Multi-turn chat completion.
        
        Default implementation converts to single prompt.
        Override for better multi-turn handling.
        """
        # Build prompt from messages
        prompt_parts = []
        system_prompt = None
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                system_prompt = content
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt = "\n".join(prompt_parts)
        
        return await self.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
