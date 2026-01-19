"""Authentication module."""

from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
    verify_password,
    get_password_hash,
)
from app.auth.oauth import google_oauth, GoogleUserInfo
from app.auth.local import authenticate_user, create_user, get_or_create_oauth_user

__all__ = [
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_token",
    "verify_password",
    "get_password_hash",
    "google_oauth",
    "GoogleUserInfo",
    "authenticate_user",
    "create_user",
    "get_or_create_oauth_user",
]
