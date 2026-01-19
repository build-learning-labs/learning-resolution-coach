"""Common utility schemas."""

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


class HealthCheck(BaseModel):
    """Health check response."""
    
    status: str = "healthy"
    service: str
    version: str = "0.1.0"


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error_code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracing")
    details: Optional[dict] = Field(default=None, description="Additional error details")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    
    items: List[T]
    total: int = Field(description="Total number of items")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=100, description="Items per page")
    pages: int = Field(description="Total number of pages")
    
    @property
    def has_next(self) -> bool:
        return self.page < self.pages
    
    @property
    def has_prev(self) -> bool:
        return self.page > 1


class SuccessResponse(BaseModel):
    """Generic success response."""
    
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[dict] = None
