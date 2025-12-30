"""
Health Check Endpoint

Provides system health status including:
- API availability
- Database connectivity (Neon Postgres)
- Vector database connectivity (Qdrant)
- OpenAI API connectivity
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from qdrant_client import QdrantClient
import openai
import time
from typing import Dict, Any

from src.config.settings import settings
from src.utils.database import SessionLocal

router = APIRouter()


async def check_postgres() -> Dict[str, Any]:
    """
    Check PostgreSQL database connectivity.

    Returns:
        dict: Status and latency information
    """
    try:
        start_time = time.time()
        db = SessionLocal()

        # Execute simple query to verify connection
        result = db.execute(text("SELECT 1")).fetchone()
        db.close()

        latency_ms = round((time.time() - start_time) * 1000, 2)

        if result and result[0] == 1:
            return {
                "status": "healthy",
                "latency_ms": latency_ms,
                "message": "PostgreSQL connection successful"
            }
        else:
            return {
                "status": "unhealthy",
                "latency_ms": latency_ms,
                "message": "PostgreSQL query returned unexpected result"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "latency_ms": None,
            "message": f"PostgreSQL connection failed: {str(e)}"
        }


async def check_qdrant() -> Dict[str, Any]:
    """
    Check Qdrant vector database connectivity.

    Returns:
        dict: Status and collection information
    """
    try:
        start_time = time.time()

        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )

        # List collections to verify connectivity
        collections = client.get_collections()
        latency_ms = round((time.time() - start_time) * 1000, 2)

        collection_names = [col.name for col in collections.collections]

        return {
            "status": "healthy",
            "latency_ms": latency_ms,
            "collections": collection_names,
            "message": f"Qdrant connected ({len(collection_names)} collections)"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "latency_ms": None,
            "collections": [],
            "message": f"Qdrant connection failed: {str(e)}"
        }


async def check_openai() -> Dict[str, Any]:
    """
    Check OpenAI API connectivity.

    Returns:
        dict: Status and API information
    """
    try:
        start_time = time.time()

        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        # List models to verify API key and connectivity
        models = client.models.list()
        latency_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "status": "healthy",
            "latency_ms": latency_ms,
            "message": "OpenAI API accessible"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "latency_ms": None,
            "message": f"OpenAI API connection failed: {str(e)}"
        }


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check system health including database and external service connectivity",
    response_description="System health status",
)
async def health_check():
    """
    Comprehensive health check endpoint.

    Checks:
    - PostgreSQL database connectivity
    - Qdrant vector database connectivity
    - OpenAI API connectivity

    Returns:
        JSONResponse: Health status with individual service checks
    """
    # Perform all health checks
    postgres_health = await check_postgres()
    qdrant_health = await check_qdrant()
    openai_health = await check_openai()

    # Determine overall system health
    all_healthy = all([
        postgres_health["status"] == "healthy",
        qdrant_health["status"] == "healthy",
        openai_health["status"] == "healthy"
    ])

    # Construct response
    response_data = {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": time.time(),
        "services": {
            "postgres": postgres_health,
            "qdrant": qdrant_health,
            "openai": openai_health
        }
    }

    # Return 200 if all services healthy, 503 if any service is down
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content=response_data,
        headers={
            "Cache-Control": "public, max-age=60",  # Cache for 60 seconds
            "Vary": "Accept-Encoding"
        }
    )


@router.get(
    "/ping",
    status_code=status.HTTP_200_OK,
    summary="Simple Ping",
    description="Lightweight ping endpoint for basic availability check",
)
async def ping():
    """
    Simple ping endpoint for quick availability check.

    Returns:
        dict: Pong response with timestamp
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "ok",
            "message": "pong",
            "timestamp": time.time()
        },
        headers={
            "Cache-Control": "public, max-age=30",  # Cache for 30 seconds
            "Vary": "Accept-Encoding"
        }
    )
