"""User-related schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user registration."""
    
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, description="User password (min 8 chars)")
    full_name: Optional[str] = Field(default=None, description="Full name")


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr = Field(description="User email address")
    password: str = Field(description="User password")


class UserResponse(BaseModel):
    """Schema for user response (excludes sensitive data)."""
    
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Token expiry in seconds")


class GoogleAuthCallback(BaseModel):
    """Schema for Google OAuth callback."""
    
    code: str = Field(description="Authorization code from Google")
    state: Optional[str] = Field(default=None, description="State parameter for CSRF protection")


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    
    email: EmailStr = Field(description="Email address for password reset")


class PasswordReset(BaseModel):
    """Schema for password reset with token."""
    
    token: str = Field(description="Password reset token")
    new_password: str = Field(min_length=8, description="New password (min 8 chars)")
