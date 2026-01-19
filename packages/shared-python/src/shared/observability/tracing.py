"""Opik tracing integration."""

import os
from functools import wraps
from typing import Optional, Any
import opik
from opik.integrations.openai import track_openai
from opik.integrations.anthropic import track_anthropic

from shared.observability import get_logger

logger = get_logger(__name__)


class TracingManager:
    """Manager for Opik tracing configuration."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TracingManager, cls).__new__(cls)
        return cls._instance
    
    def configure(
        self,
        project_name: str = "learning-resolution-coach",
        api_key: Optional[str] = None,
    ):
        """Configure Opik tracing."""
        if self._initialized:
            return
            
        api_key = api_key or os.getenv("OPIK_API_KEY")
        if not api_key:
            logger.warning("OPIK_API_KEY not found. Tracing disabled.")
            return
        
        try:
            opik.configure(
                api_key=api_key,
                use_local=False,
                force=True,
                automatic_approvals=True,
            )
            self._initialized = True
            logger.info("Opik tracing initialized", project=project_name)
        except Exception as e:
            logger.error("Failed to initialize Opik", error=str(e))

    def track_llm_client(self, client: Any):
        """ instrument an LLM client."""
        if not self._initialized:
            return client
            
        try:
            # Auto-instrumentation based on client type
            if "OpenAI" in str(type(client)):
                return track_openai(client)
            elif "Anthropic" in str(type(client)):
                return track_anthropic(client)
            return client
        except Exception as e:
            logger.warning("Failed to instrument LLM client", error=str(e))
            return client


def trace_function(name: Optional[str] = None, tags: Optional[list] = None):
    """Decorator to trace a function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not TracingManager()._initialized:
                return func(*args, **kwargs)
                
            try:
                # Use Opik's native track decorator functionality manually
                # or just rely on auto-instrumentation if this is too complex
                # For now, we'll use the opik.track if available
                return opik.track(name=name, tags=tags)(func)(*args, **kwargs)
            except Exception:
                return func(*args, **kwargs)
        return wrapper
    return decorator


tracing = TracingManager()
