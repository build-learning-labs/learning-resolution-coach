"""Google OAuth 2.0 + OIDC implementation."""

from typing import Optional
import httpx
from pydantic import BaseModel

from app.core.config import settings


class GoogleUserInfo(BaseModel):
    """Google user information from OIDC."""
    
    id: str
    email: str
    verified_email: bool = False
    name: Optional[str] = None
    picture: Optional[str] = None


class GoogleOAuth:
    """Google OAuth 2.0 client."""
    
    AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        """Initialize Google OAuth client.
        
        Args:
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
            redirect_uri: OAuth redirect URI
        """
        self.client_id = client_id or settings.GOOGLE_CLIENT_ID
        self.client_secret = client_secret or settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = redirect_uri or settings.GOOGLE_REDIRECT_URI
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Get Google OAuth authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL to redirect user to
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        
        if state:
            params["state"] = state
        
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTHORIZE_URL}?{query}"
    
    async def exchange_code(self, code: str) -> dict:
        """Exchange authorization code for tokens.
        
        Args:
            code: Authorization code from Google
            
        Returns:
            Token response with access_token, refresh_token, id_token
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
            )
            response.raise_for_status()
            return response.json()
    
    async def get_user_info(self, access_token: str) -> GoogleUserInfo:
        """Get user information from Google.
        
        Args:
            access_token: Google access token
            
        Returns:
            GoogleUserInfo with user details
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
            
            return GoogleUserInfo(
                id=data["id"],
                email=data["email"],
                verified_email=data.get("verified_email", False),
                name=data.get("name"),
                picture=data.get("picture"),
            )
    
    async def authenticate(self, code: str) -> GoogleUserInfo:
        """Full authentication flow: exchange code and get user info.
        
        Args:
            code: Authorization code from Google
            
        Returns:
            GoogleUserInfo with authenticated user details
        """
        tokens = await self.exchange_code(code)
        return await self.get_user_info(tokens["access_token"])


# Singleton instance
google_oauth = GoogleOAuth()
