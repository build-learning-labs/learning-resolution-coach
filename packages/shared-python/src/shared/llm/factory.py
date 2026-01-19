"""LLM provider factory."""

import os
from typing import Optional
from shared.llm.base import LLMProvider


def get_llm_provider(
    provider: Optional[str] = None,
    **kwargs,
) -> LLMProvider:
    """Factory function to get the appropriate LLM provider.
    
    Args:
        provider: Provider name (openai, anthropic, azure, ollama)
                  If None, uses LLM_PROVIDER env var
        **kwargs: Provider-specific configuration
        
    Returns:
        Configured LLM provider instance
        
    Raises:
        ValueError: If provider is not supported
    """
    if provider is None:
        provider = os.getenv("LLM_PROVIDER", "openai")
    
    provider = provider.lower()
    
    if provider == "openai":
        from shared.llm.openai import OpenAIProvider
        
        return OpenAIProvider(
            api_key=kwargs.get("api_key") or os.getenv("OPENAI_API_KEY"),
            model=kwargs.get("model") or os.getenv("OPENAI_MODEL", "gpt-4o"),
            base_url=kwargs.get("base_url"),
        )
    
    elif provider == "anthropic":
        from shared.llm.anthropic import AnthropicProvider
        
        return AnthropicProvider(
            api_key=kwargs.get("api_key") or os.getenv("ANTHROPIC_API_KEY"),
            model=kwargs.get("model") or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
        )
    
    elif provider == "azure":
        from shared.llm.azure import AzureOpenAIProvider
        
        return AzureOpenAIProvider(
            endpoint=kwargs.get("endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=kwargs.get("api_key") or os.getenv("AZURE_OPENAI_KEY"),
            deployment=kwargs.get("deployment") or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        )
    
    elif provider == "ollama":
        from shared.llm.ollama import OllamaProvider
        
        return OllamaProvider(
            base_url=kwargs.get("base_url") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=kwargs.get("model") or os.getenv("OLLAMA_MODEL", "llama3.2"),
        )
    
    else:
        supported = ["openai", "anthropic", "azure", "ollama"]
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers: {supported}"
        )
