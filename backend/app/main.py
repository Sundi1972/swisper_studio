"""SwisperStudio FastAPI Application"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import close_db_connection, create_db_and_tables, get_async_session_factory
from app.api.routes import (
    auth,
    users,
    traces,
    observations,
    projects,
    model_pricing,
    system_architecture,
    mock_sap,
    environments,
    config_versions,
)
from app.api.deps import APIKey

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events"""
    # Startup
    # Note: Database tables are managed by Alembic migrations, not auto-created
    
    # Start observability consumer (if enabled)
    consumer = None
    consumer_task = None
    
    if settings.OBSERVABILITY_ENABLED:
        try:
            from app.services.observability_consumer import ObservabilityConsumer
            
            consumer = ObservabilityConsumer(
                redis_url=settings.OBSERVABILITY_REDIS_URL,
                db_session_factory=get_async_session_factory(),
                stream_name=settings.OBSERVABILITY_STREAM_NAME,
                group_name=settings.OBSERVABILITY_GROUP_NAME,
                consumer_name=settings.OBSERVABILITY_CONSUMER_NAME,
                batch_size=settings.OBSERVABILITY_BATCH_SIZE,
            )
            
            # Start consumer in background task
            consumer_task = asyncio.create_task(consumer.start())
            logger.info("✅ Observability consumer started")
            logger.info(f"   Consuming from: {settings.OBSERVABILITY_REDIS_URL}")
            logger.info(f"   Stream: {settings.OBSERVABILITY_STREAM_NAME}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start observability consumer: {e}")
            logger.warning("   Continuing without consumer - events will queue")
    else:
        logger.info("ℹ️ Observability consumer disabled (OBSERVABILITY_ENABLED=False)")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Stop observability consumer
    if consumer:
        try:
            await consumer.stop()
            if consumer_task:
                consumer_task.cancel()
                try:
                    await consumer_task
                except asyncio.CancelledError:
                    pass
            logger.info("✅ Observability consumer stopped")
        except Exception as e:
            logger.error(f"⚠️ Error stopping observability consumer: {e}")
    
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
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)  # Auth (no tags, already defined in router)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)  # User management (tags in router)
app.include_router(projects.router, prefix=settings.API_V1_PREFIX, tags=["projects"])
app.include_router(environments.router, prefix=settings.API_V1_PREFIX, tags=["environments"])
app.include_router(config_versions.router, prefix=settings.API_V1_PREFIX, tags=["config-versions"])
app.include_router(traces.router, prefix=settings.API_V1_PREFIX, tags=["traces"])
app.include_router(observations.router, prefix=settings.API_V1_PREFIX, tags=["observations"])
app.include_router(model_pricing.router, prefix=settings.API_V1_PREFIX, tags=["model-pricing"])
app.include_router(system_architecture.router, prefix=settings.API_V1_PREFIX, tags=["system-architecture"])
app.include_router(mock_sap.router, prefix=f"{settings.API_V1_PREFIX}/mock-swisper/api/admin/config", tags=["mock-sap"])


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
