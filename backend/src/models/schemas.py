"""
Pydantic schemas for API request/response validation.

Defines schemas for chat requests, SSE events, and health checks
according to the OpenAPI 3.1 specification.
"""
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# ==================== Chat Schemas ====================

class ChatRequest(BaseModel):
    """
    Request schema for POST /api/chat endpoint.

    Represents a user's question submitted to the chatbot.
    Includes input sanitization to prevent injection attacks.
    """
    session_id: UUID = Field(
        ...,
        description="Browser session identifier (generated client-side)"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's question or message"
    )
    selected_text: Optional[str] = Field(
        None,
        max_length=5000,
        description="Text selected by user for contextual Q&A (P3 feature)"
    )
    conversation_id: Optional[UUID] = Field(
        None,
        description="Existing conversation ID for follow-up questions (null for new conversation)"
    )

    @field_validator('message')
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        """
        Sanitize user message to prevent injection attacks.

        - Strips leading/trailing whitespace
        - Removes null bytes
        - Removes control characters (except newlines and tabs)
        - Validates message is not empty after sanitization

        Args:
            v: Raw user message

        Returns:
            Sanitized message

        Raises:
            ValueError: If message is empty after sanitization
        """
        # Strip whitespace
        v = v.strip()

        # Remove null bytes
        v = v.replace('\x00', '')

        # Remove control characters except \n (newline) and \t (tab)
        v = ''.join(char for char in v if char == '\n' or char == '\t' or ord(char) >= 32)

        # Validate not empty
        if not v:
            raise ValueError('Message cannot be empty after sanitization')

        return v

    @field_validator('selected_text')
    @classmethod
    def sanitize_selected_text(cls, v: Optional[str]) -> Optional[str]:
        """
        Sanitize selected text to prevent injection attacks.

        Args:
            v: Raw selected text

        Returns:
            Sanitized selected text or None
        """
        if v is None:
            return None

        # Strip whitespace
        v = v.strip()

        # Remove null bytes
        v = v.replace('\x00', '')

        # Remove control characters except \n and \t
        v = ''.join(char for char in v if char == '\n' or char == '\t' or ord(char) >= 32)

        # Return None if empty after sanitization
        return v if v else None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "message": "How do I calculate inverse kinematics for a 6-DOF robot arm?",
                    "selected_text": None,
                    "conversation_id": None
                }
            ]
        }
    }


class TokenEvent(BaseModel):
    """
    SSE event schema for streaming LLM tokens.

    Event type: 'token'
    """
    token: str = Field(
        ...,
        description="Individual LLM output token"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"token": "kinematics"}
            ]
        }
    }


class CitationEvent(BaseModel):
    """
    SSE event schema for content citations.

    Event type: 'citation'
    """
    chunk_id: UUID = Field(
        ...,
        description="UUID of the referenced content chunk"
    )
    chapter: str = Field(
        ...,
        description="Chapter title"
    )
    section: str = Field(
        ...,
        description="Section heading"
    )
    url: str = Field(
        ...,
        description="Docusaurus URL path to the content"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
                    "chapter": "Robot Kinematics",
                    "section": "2.3 Inverse Kinematics",
                    "url": "/chapters/02-kinematics#inverse-kinematics"
                }
            ]
        }
    }


class DoneEvent(BaseModel):
    """
    SSE event schema for completion signal.

    Event type: 'done'
    Signals end of streaming response and provides conversation/message IDs.
    """
    conversation_id: UUID = Field(
        ...,
        description="Conversation ID (for follow-up questions)"
    )
    message_id: UUID = Field(
        ...,
        description="Message ID of the assistant's response"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                    "message_id": "a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6"
                }
            ]
        }
    }


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """
    Schema for error responses.

    Used for 400, 429, and 500 status codes.
    """
    error: str = Field(
        ...,
        description="Error type/code"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error context"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "ValidationError",
                    "message": "Message exceeds maximum length of 2000 characters",
                    "details": {
                        "field": "message",
                        "constraint": "max_length"
                    }
                }
            ]
        }
    }


# ==================== Health Check Schemas ====================

class ServiceStatus(BaseModel):
    """
    Status of individual service dependencies.
    """
    database: str = Field(
        ...,
        description="Neon Postgres connection status",
        pattern="^(ok|error)$"
    )
    vector_db: str = Field(
        ...,
        description="Qdrant connection status",
        pattern="^(ok|error)$"
    )
    openai: str = Field(
        ...,
        description="OpenAI API connectivity",
        pattern="^(ok|error)$"
    )


class HealthResponse(BaseModel):
    """
    Schema for GET /api/health endpoint.

    Returns health status of the API and its dependencies.
    """
    status: str = Field(
        ...,
        description="Overall health status",
        pattern="^(healthy|unhealthy)$"
    )
    services: ServiceStatus = Field(
        ...,
        description="Status of individual service dependencies"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of health check"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "services": {
                        "database": "ok",
                        "vector_db": "ok",
                        "openai": "ok"
                    },
                    "timestamp": "2025-12-26T14:30:00Z"
                }
            ]
        }
    }
