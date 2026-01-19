"""Gateway API - Main Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from shared.observability import RequestIdMiddleware, setup_logging, get_logger
from app.core.config import settings
from app.routes import auth, health, proxy


# Setup logging
setup_logging(
    level=settings.LOG_LEVEL,
    json_format=settings.ENVIRONMENT != "development",
    service_name="gateway",
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Gateway service starting", port=settings.GATEWAY_PORT)
    yield
    logger.info("Gateway service shutting down")


app = FastAPI(
    title="Learning Resolution Coach - Gateway",
    description="API Gateway with authentication and routing",
    version="0.1.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(proxy.router, prefix="/api", tags=["API Proxy"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Learning Resolution Coach Gateway",
        "version": "0.1.0",
        "docs": "/docs",
    }
