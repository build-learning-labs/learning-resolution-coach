"""Gemini LLM provider implementation (Replacing OpenAI for Hackathon)."""

import json
import os
from typing import AsyncGenerator, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from shared.llm.base import LLMProvider, LLMResponse

class OpenAIProvider(LLMProvider):
    """
    NOTE: This class is named OpenAIProvider to maintain compatibility 
    with the existing Factory logic, but it uses Google Gemini internally.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-1.5-flash",
        base_url: Optional[str] = None,
    ):
        """Initialize Gemini provider."""
        # Prioritize Google API Key from Env if not passed directly
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            # Fallback: Try to grab OpenAI key if user forgot to set Google one
            self.api_key = os.getenv("OPENAI_API_KEY")

        genai.configure(api_key=self.api_key)

        # Ensure we are using a valid Gemini model name
        if "gpt" in model:
            self.model_name = "gemini-1.5-flash"
        else:
            self.model_name = model

    @property
    def provider_name(self) -> str:
        return "google"

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> LLMResponse:

        # Configure the model
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        # Initialize model with system prompt if present
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt if system_prompt else None
        )

        # Generate
        try:
            response = await model.generate_content_async(
                prompt,
                generation_config=generation_config
            )

            content = response.text

            return LLMResponse(
                content=content,
                model=self.model_name,
                usage={
                    "prompt_tokens": 0, # Gemini doesn't always return token counts easily
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
                finish_reason="stop",
            )
        except Exception as e:
            # Fallback for safety blocks or errors
            print(f"Gemini Error: {e}")
            return LLMResponse(content=f"Error: {str(e)}", model=self.model_name)

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:

        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt
        )

        response_stream = await model.generate_content_async(
            prompt,
            generation_config=generation_config,
            stream=True
        )

        async for chunk in response_stream:
            if chunk.text:
                yield chunk.text

    async def structured_output(
        self,
        prompt: str,
        schema: dict,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        **kwargs: Any,
    ) -> dict:

        # Gemini JSON Mode
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json"
        )

        # Add schema hint to system prompt
        schema_text = json.dumps(schema)
        full_system_prompt = f"{system_prompt or ''}\n\nFollow this JSON schema:\n{schema_text}"

        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=full_system_prompt
        )

        try:
            response = await model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            return json.loads(response.text)
        except Exception:
            return {}
