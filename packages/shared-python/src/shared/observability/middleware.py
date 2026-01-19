"""Request ID middleware for tracing."""

import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable to store request ID across async calls
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Get current request ID from context."""
    return request_id_var.get()


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to inject and propagate request IDs.
    
    - Checks for X-Request-ID header from client/gateway
    - Generates new UUID if not present
    - Adds X-Request-ID to response headers
    - Stores in context variable for logging
    """
    
    HEADER_NAME = "X-Request-ID"
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Get existing request ID or generate new one
        request_id = request.headers.get(self.HEADER_NAME)
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Store in context variable
        token = request_id_var.set(request_id)
        
        try:
            # Add to request state for access in routes
            request.state.request_id = request_id
            
            # Process request
            response = await call_next(request)
            
            # Add to response headers
            response.headers[self.HEADER_NAME] = request_id
            
            return response
        finally:
            # Reset context variable
            request_id_var.reset(token)
