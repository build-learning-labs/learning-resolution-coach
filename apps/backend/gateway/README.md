# 🚪 API Gateway

The unified entry point for the LRC platform. Handles authentication, request routing, and rate limiting.

## 🚀 Role
- **Direct Entry**: [http://localhost:8000](http://localhost:8000)
- **Auth**: Implements Google OAuth2 and JWT-based session management.
- **Routing**: Proxies requests to internal microservices.

## 🛠️ Tech Stack
- FastAPI
- Pydantic V2
- Python-jose (JWT)
