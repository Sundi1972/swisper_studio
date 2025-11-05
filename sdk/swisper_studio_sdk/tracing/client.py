"""
SwisperStudio API client

Handles communication with SwisperStudio backend for trace ingestion.

v0.2.1: Added fire-and-forget support for zero-latency observability.
"""

import asyncio
import httpx
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Global client instance
_studio_client: Optional['SwisperStudioClient'] = None


class SwisperStudioClient:
    """Client for SwisperStudio API"""

    def __init__(self, api_url: str, api_key: str, project_id: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.project_id = project_id
        self.client = httpx.AsyncClient(
            base_url=api_url,
            headers={"X-API-Key": api_key},
            timeout=5.0,
        )

    async def create_trace(
        self,
        name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new trace"""
        trace_id = str(uuid.uuid4())

        await self.client.post(
            "/api/v1/traces",
            json={
                "id": trace_id,
                "project_id": self.project_id,
                "name": name,
                "user_id": user_id,
                "session_id": session_id,
                "meta": meta or {},
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return trace_id

    async def create_observation(
        self,
        trace_id: str,
        name: str,
        type: str,
        parent_observation_id: Optional[str] = None,
        input: Optional[Dict[str, Any]] = None,
        observation_id: Optional[str] = None,  # NEW: Accept pre-generated ID
    ) -> str:
        """
        Create a new observation.
        
        Args:
            observation_id: Pre-generated ID (for fire-and-forget pattern)
        
        Returns:
            observation_id (either generated or provided)
        """
        obs_id = observation_id or str(uuid.uuid4())

        await self.client.post(
            "/api/v1/observations",
            json={
                "id": obs_id,
                "trace_id": trace_id,
                "parent_observation_id": parent_observation_id,
                "name": name,
                "type": type,
                "input": input,
                "start_time": datetime.utcnow().isoformat(),
            }
        )

        return obs_id
    
    def create_observation_background(
        self,
        trace_id: str,
        name: str,
        type: str,
        observation_id: str,  # Required for fire-and-forget
        parent_observation_id: Optional[str] = None,
        input: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Create observation in background (fire-and-forget, non-blocking).
        
        This is the recommended method for production use.
        Zero latency impact - HTTP happens in background.
        """
        asyncio.create_task(self._create_observation_async(
            trace_id, name, type, observation_id, parent_observation_id, input
        ))
    
    async def _create_observation_async(
        self,
        trace_id: str,
        name: str,
        type: str,
        observation_id: str,
        parent_observation_id: Optional[str],
        input: Optional[Dict[str, Any]],
    ) -> None:
        """Background task for creating observation"""
        try:
            await self.client.post(
                "/api/v1/observations",
                json={
                    "id": observation_id,
                    "trace_id": trace_id,
                    "parent_observation_id": parent_observation_id,
                    "name": name,
                    "type": type,
                    "input": input,
                    "start_time": datetime.utcnow().isoformat(),
                }
            )
        except Exception as e:
            # Silent failure - log but don't crash app
            logger.debug(f"Background observation creation failed: {e}")

    async def end_observation(
        self,
        observation_id: str,
        output: Optional[Dict[str, Any]] = None,
        level: str = "DEFAULT",
        status_message: Optional[str] = None,
    ) -> None:
        """End an observation"""
        await self.client.patch(
            f"/api/v1/observations/{observation_id}",
            json={
                "end_time": datetime.utcnow().isoformat(),
                "output": output,
                "level": level,
                "status_message": status_message,
            }
        )
    
    def end_observation_background(
        self,
        observation_id: str,
        output: Optional[Dict[str, Any]] = None,
        level: str = "DEFAULT",
        status_message: Optional[str] = None,
    ) -> None:
        """
        End observation in background (fire-and-forget, non-blocking).
        
        Zero latency impact - HTTP happens in background.
        """
        asyncio.create_task(self._end_observation_async(
            observation_id, output, level, status_message
        ))
    
    async def _end_observation_async(
        self,
        observation_id: str,
        output: Optional[Dict[str, Any]],
        level: str,
        status_message: Optional[str],
    ) -> None:
        """Background task for ending observation"""
        try:
            await self.client.patch(
                f"/api/v1/observations/{observation_id}",
                json={
                    "end_time": datetime.utcnow().isoformat(),
                    "output": output,
                    "level": level,
                    "status_message": status_message,
                }
            )
        except Exception as e:
            # Silent failure - log but don't crash app
            logger.debug(f"Background observation end failed: {e}")


def initialize_tracing(
    api_url: str,
    api_key: str,
    project_id: str,
    enabled: bool = True,
) -> None:
    """
    Initialize tracing (call once at startup)
    
    Args:
        api_url: SwisperStudio API URL (e.g., "https://studio.swisper.com")
        api_key: SwisperStudio API key
        project_id: Project ID in SwisperStudio
        enabled: Whether tracing is enabled
    """
    global _studio_client
    if enabled:
        _studio_client = SwisperStudioClient(
            api_url=api_url,
            api_key=api_key,
            project_id=project_id,
        )


def get_studio_client() -> Optional[SwisperStudioClient]:
    """Get the global studio client"""
    return _studio_client

