"""Azure OpenAI LLM provider implementation."""

import json
from typing import AsyncGenerator, Any, Optional
from openai import AsyncAzureOpenAI
from shared.llm.base import LLMProvider, LLMResponse


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI API provider."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        deployment: str = "gpt-4o",
        api_version: str = "2024-02-15-preview",
    ):
        """Initialize Azure OpenAI provider.
        
        Args:
            endpoint: Azure OpenAI endpoint URL
            api_key: Azure OpenAI API key
            deployment: Deployment name
            api_version: API version
        """
        self.deployment = deployment
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )

    @property
    def provider_name(self) -> str:
        return "azure"

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> LLMResponse:
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        
        choice = response.choices[0]
        
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            finish_reason=choice.finish_reason,
        )

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        stream = await self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def structured_output(
        self,
        prompt: str,
        schema: dict,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        **kwargs: Any,
    ) -> dict:
        messages = []
        
        schema_instruction = (
            f"Respond with valid JSON matching this schema:\n"
            f"```json\n{json.dumps(schema, indent=2)}\n```\n"
            f"Only output the JSON, no other text."
        )
        
        full_system = schema_instruction
        if system_prompt:
            full_system = f"{system_prompt}\n\n{schema_instruction}"
        
        messages.append({"role": "system", "content": full_system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
                **kwargs,
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except Exception:
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=temperature,
                **kwargs,
            )
            content = response.choices[0].message.content or "{}"
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                raise ValueError(f"Could not parse JSON from response: {content}")
