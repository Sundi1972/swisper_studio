"""SwisperStudio FastAPI Application"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import close_db_connection, create_db_and_tables
from app.api.routes import traces, observations, projects
from app.api.deps import APIKey


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events"""
    # Startup
    # Note: Database tables are managed by Alembic migrations, not auto-created
    
    yield
    
    # Shutdown
    await close_db_connection()


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix=settings.API_V1_PREFIX, tags=["projects"])
app.include_router(traces.router, prefix=settings.API_V1_PREFIX, tags=["traces"])
app.include_router(observations.router, prefix=settings.API_V1_PREFIX, tags=["observations"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.VERSION}


@app.get("/api/health")
async def health_check_api(api_key: APIKey) -> dict[str, str]:
    """
    Health check endpoint with authentication (for login validation).
    
    This endpoint requires API key authentication, making it suitable
    for validating credentials during login.
    """
    return {"status": "healthy", "version": settings.VERSION, "authenticated": "true"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {
        "message": "SwisperStudio API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }
