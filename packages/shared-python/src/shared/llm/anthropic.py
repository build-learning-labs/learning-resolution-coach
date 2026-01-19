"""Anthropic LLM provider implementation."""

import json
from typing import AsyncGenerator, Any, Optional
from anthropic import AsyncAnthropic
from shared.llm.base import LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    """Anthropic API provider (Claude models)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
    ):
        """Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key (or from ANTHROPIC_API_KEY env var)
            model: Model to use (default: claude-3-5-sonnet)
        """
        self.model = model
        self.client = AsyncAnthropic(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> LLMResponse:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            **kwargs,
        )
        
        content = ""
        if response.content:
            content = response.content[0].text if response.content else ""
        
        return LLMResponse(
            content=content,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            finish_reason=response.stop_reason,
        )

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            **kwargs,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def structured_output(
        self,
        prompt: str,
        schema: dict,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        **kwargs: Any,
    ) -> dict:
        schema_instruction = (
            f"Respond with valid JSON matching this schema:\n"
            f"```json\n{json.dumps(schema, indent=2)}\n```\n"
            f"Only output the JSON, no other text."
        )
        
        full_system = schema_instruction
        if system_prompt:
            full_system = f"{system_prompt}\n\n{schema_instruction}"
        
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=full_system,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            **kwargs,
        )
        
        content = response.content[0].text if response.content else "{}"
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Could not parse JSON from response: {content}")
