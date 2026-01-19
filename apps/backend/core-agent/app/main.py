"""Core Agent API - Main Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.observability import RequestIdMiddleware, setup_logging, get_logger, tracing
from app.core.config import settings
from app.api.v1 import routes


setup_logging(
    level=settings.LOG_LEVEL,
    json_format=settings.ENVIRONMENT != "development",
    service_name="core-agent",
)

# Initialize tracing
tracing.configure(
    project_name=settings.OPIK_PROJECT,
    api_key=settings.OPIK_API_KEY,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Core Agent service starting", port=settings.CORE_AGENT_PORT)
    yield
    logger.info("Core Agent service shutting down")


app = FastAPI(
    title="Learning Resolution Coach - Core Agent",
    description="Planning, check-ins, and memory rules",
    version="0.1.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Gateway handles CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(routes.router, prefix="/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "core-agent"}
