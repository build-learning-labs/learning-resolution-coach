"""API proxy routes to backend services."""

import httpx
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.auth.jwt import verify_token


router = APIRouter()


# Service URL mapping
SERVICE_URLS = {
    "agent": settings.CORE_AGENT_URL,
    "rag": settings.RAG_WORKER_URL,
    "eval": settings.EVALUATOR_URL,
    "notification": settings.NOTIFICATION_URL,
}


async def get_current_user_id(request: Request) -> int:
    """Extract and validate user ID from Authorization header."""
    if request.method == "OPTIONS":
        return 0
    
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(" ")[1]
    token_data = verify_token(token, token_type="access")
    
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token_data.user_id


async def proxy_request(
    service: str,
    path: str,
    request: Request,
    user_id: int,
):
    """Proxy request to backend service."""
    if request.method == "OPTIONS":
        from fastapi.responses import Response
        return Response(status_code=200)

    if service not in SERVICE_URLS:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    
    service_url = SERVICE_URLS[service]
    target_url = f"{service_url}{path}"
    
    # Get request body if present
    body = await request.body()
    
    # Forward headers (excluding host)
    headers = dict(request.headers)
    headers.pop("host", None)
    headers["X-User-ID"] = str(user_id)
    headers["X-Request-ID"] = getattr(request.state, "request_id", "")
    
    # Make request to backend service
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=dict(request.query_params),
            )
            
            return StreamingResponse(
                content=response.iter_bytes(),
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail=f"Service '{service}' is unavailable",
            )


# Agent service routes
@router.api_route("/v1/intake", methods=["POST"])
@router.api_route("/v1/premortem", methods=["POST"])
@router.api_route("/v1/plan/{path:path}", methods=["GET", "POST", "OPTIONS"])
@router.api_route("/v1/commitment/{path:path}", methods=["GET", "OPTIONS"])
@router.api_route("/v1/tasks/{path:path}", methods=["GET", "POST", "PUT", "OPTIONS"])
@router.api_route("/v1/checkin/{path:path}", methods=["GET", "POST", "OPTIONS"])
@router.api_route("/v1/metrics/{path:path}", methods=["GET", "OPTIONS"])
async def agent_proxy(
    request: Request,
    user_id: int = Depends(get_current_user_id),
):
    """Proxy to Core Agent service."""
    path = request.url.path.replace("/api", "")
    return await proxy_request("agent", path, request, user_id)


# RAG service routes  
@router.api_route("/v1/retrieve", methods=["POST"])
@router.api_route("/v1/resources/{path:path}", methods=["GET", "POST"])
async def rag_proxy(
    request: Request,
    user_id: int = Depends(get_current_user_id),
):
    """Proxy to RAG Worker service."""
    path = request.url.path.replace("/api", "")
    return await proxy_request("rag", path, request, user_id)


# Evaluator service routes
@router.api_route("/v1/eval/{path:path}", methods=["GET", "POST"])
@router.api_route("/v1/quiz/{path:path}", methods=["GET", "POST"])
@router.api_route("/v1/coding/{path:path}", methods=["GET", "POST"])
async def eval_proxy(
    request: Request,
    user_id: int = Depends(get_current_user_id),
):
    """Proxy to Evaluator service."""
    path = request.url.path.replace("/api", "")
    return await proxy_request("eval", path, request, user_id)
