"""
Chat API endpoint with RAG-powered streaming responses.

Endpoints:
- POST /api/chat: Submit question and stream response with citations
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.models.schemas import ChatRequest
from src.models.conversation import Conversation, Message
from src.services.rag import RAGPipeline
from src.services.llm import StreamingLLM, SSEFormatter
from src.utils.database import get_db
from src.utils.app_logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ==================== Rate Limiting ====================

class RateLimiter:
    """
    Simple in-memory rate limiter for chat requests.

    Limits requests per session to prevent abuse.
    """

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.logger = get_logger(__name__)

    def is_allowed(self, session_id: str) -> bool:
        """
        Check if request is allowed for session.

        Args:
            session_id: Session identifier

        Returns:
            True if allowed, False if rate limited
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)

        # Remove old requests outside window
        self.requests[session_id] = [
            ts for ts in self.requests[session_id]
            if ts > window_start
        ]

        # Check if under limit
        if len(self.requests[session_id]) >= self.max_requests:
            self.logger.warning(
                f"Rate limit exceeded for session {session_id}",
                extra={"extra_fields": {"session_id": session_id}}
            )
            return False

        # Add current request
        self.requests[session_id].append(now)
        return True

    def cleanup_old_sessions(self):
        """Remove sessions with no recent requests."""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds * 2)

        sessions_to_remove = []
        for session_id, timestamps in self.requests.items():
            if not timestamps or all(ts < cutoff for ts in timestamps):
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            del self.requests[session_id]


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


# ==================== Conversation Helpers ====================

def get_or_create_conversation(
    db: Session,
    conversation_id: Optional[uuid.UUID],
    session_id: uuid.UUID
) -> Conversation:
    """
    Get existing conversation or create new one.

    Args:
        db: Database session
        conversation_id: Existing conversation ID (None for new)
        session_id: Browser session ID

    Returns:
        Conversation object
    """
    if conversation_id:
        # Try to get existing conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.session_id == str(session_id)
        ).first()

        if conversation:
            return conversation
        else:
            logger.warning(
                f"Conversation {conversation_id} not found, creating new one"
            )

    # Create new conversation
    conversation = Conversation(session_id=str(session_id))
    db.add(conversation)
    db.flush()  # Get ID without committing

    logger.info(f"Created new conversation {conversation.id}")
    return conversation


def save_user_message(
    db: Session,
    conversation: Conversation,
    message: str,
    selected_text: Optional[str] = None
) -> Message:
    """
    Save user message to database.

    Args:
        db: Database session
        conversation: Parent conversation
        message: User message content
        selected_text: Optional selected text

    Returns:
        Message object
    """
    msg = Message(
        conversation_id=conversation.id,
        role='user',
        content=message,
        selected_text=selected_text
    )
    db.add(msg)
    db.flush()

    logger.info(f"Saved user message {msg.id}")
    return msg


def save_assistant_message(
    db: Session,
    conversation: Conversation,
    content: str,
    cited_chunk_ids: list
) -> Message:
    """
    Save assistant message to database.

    Args:
        db: Database session
        conversation: Parent conversation
        content: Assistant response content
        cited_chunk_ids: List of cited chunk UUIDs

    Returns:
        Message object
    """
    msg = Message(
        conversation_id=conversation.id,
        role='assistant',
        content=content,
        cited_chunks=[str(cid) for cid in cited_chunk_ids]
    )
    db.add(msg)
    db.flush()

    logger.info(f"Saved assistant message {msg.id} with {len(cited_chunk_ids)} citations")
    return msg


def get_conversation_history(
    db: Session,
    conversation: Conversation,
    max_messages: int = 10
) -> list:
    """
    Get recent conversation history.

    Args:
        db: Database session
        conversation: Conversation object
        max_messages: Maximum number of messages to retrieve

    Returns:
        List of (role, content) tuples
    """
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(
        Message.created_at.asc()
    ).limit(max_messages).all()

    history = [(msg.role, msg.content) for msg in messages]

    logger.info(f"Retrieved {len(history)} messages from conversation history")
    return history


# ==================== Chat Endpoint ====================

@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Handle chat request with streaming response.

    Request Body:
    - session_id: Browser session UUID
    - message: User's question
    - selected_text: Optional selected text for context
    - conversation_id: Optional existing conversation ID

    Response:
    - Server-Sent Events (SSE) stream with:
      - token events: Individual LLM output tokens
      - citation events: Source citations
      - done event: Completion with conversation/message IDs

    Rate Limiting:
    - 10 requests per minute per session

    Errors:
    - 429: Rate limit exceeded
    - 500: Internal server error
    """
    session_id_str = str(request.session_id)

    # Check rate limit
    if not rate_limiter.is_allowed(session_id_str):
        logger.warning(
            f"Rate limit exceeded for session {session_id_str}",
            extra={"extra_fields": {"session_id": session_id_str}}
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before sending more requests."
        )

    logger.info(
        f"Chat request from session {session_id_str}: {request.message[:100]}...",
        extra={
            "extra_fields": {
                "session_id": session_id_str,
                "message_length": len(request.message),
                "has_selected_text": request.selected_text is not None,
                "conversation_id": str(request.conversation_id) if request.conversation_id else None
            }
        }
    )

    # Get or create conversation
    conversation = get_or_create_conversation(
        db,
        request.conversation_id,
        request.session_id
    )

    # Save user message
    user_message = save_user_message(
        db,
        conversation,
        request.message,
        request.selected_text
    )

    # Get conversation history
    history = get_conversation_history(db, conversation)

    # Initialize services
    rag_pipeline = RAGPipeline()
    streaming_llm = StreamingLLM()

    async def event_generator():
        """Generate SSE events for streaming response."""
        try:
            # Process query with RAG pipeline
            logger.info("Processing RAG query")
            messages, chunks = rag_pipeline.process_query(
                query=request.message,
                selected_text=request.selected_text,
                conversation_history=history,
                optimize_tokens=True
            )

            # Stream LLM response
            logger.info("Starting LLM streaming")
            async for event in streaming_llm.stream_response(messages, chunks):
                event_type = event["type"]
                event_data = event["data"]

                # Format as SSE
                if event_type == "token":
                    sse = SSEFormatter.format_token(event_data["token"])
                elif event_type == "citation":
                    sse = SSEFormatter.format_citation(
                        event_data["chunk_id"],
                        event_data["chapter"],
                        event_data["section"],
                        event_data["url"]
                    )
                elif event_type == "error":
                    sse = SSEFormatter.format_error(
                        event_data["error"],
                        event_data["message"]
                    )
                else:
                    continue

                yield sse

            # Get complete response and citations
            complete_response = streaming_llm.get_last_response()
            cited_chunks = streaming_llm.get_last_cited_chunks()

            # Save assistant message
            cited_chunk_ids = [chunk.chunk_id for chunk in cited_chunks]
            assistant_message = save_assistant_message(
                db,
                conversation,
                complete_response or "",
                cited_chunk_ids
            )

            # Commit all changes
            db.commit()

            # Send done event
            done_sse = SSEFormatter.format_done(
                str(conversation.id),
                str(assistant_message.id)
            )
            yield done_sse

            logger.info(
                f"Chat request completed successfully",
                extra={
                    "extra_fields": {
                        "conversation_id": str(conversation.id),
                        "message_id": str(assistant_message.id),
                        "num_citations": len(cited_chunk_ids)
                    }
                }
            )

        except Exception as e:
            logger.error(f"Error in chat endpoint: {e}", exc_info=True)

            # Send error event
            error_sse = SSEFormatter.format_error(
                "InternalError",
                "An error occurred while processing your request. Please try again."
            )
            yield error_sse

            # Rollback database changes
            db.rollback()

    # Return streaming response
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering in nginx
        }
    )


# ==================== Health Check ====================

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for chat service.

    Returns:
    - status: Service health status
    - services: Status of dependencies (database, vector_db, openai)
    """
    from src.config.settings import get_settings
    from qdrant_client import QdrantClient
    from openai import AsyncOpenAI

    settings = get_settings()
    services_status = {
        "database": "ok",
        "vector_db": "ok",
        "openai": "ok"
    }

    # Check database
    try:
        db.execute("SELECT 1")
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        services_status["database"] = "error"

    # Check Qdrant
    try:
        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        client.get_collections()
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        services_status["vector_db"] = "error"

    # Check OpenAI (simple API key validation)
    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        # Note: We don't make an actual API call to avoid costs
        # Just verify the client can be initialized
    except Exception as e:
        logger.error(f"OpenAI health check failed: {e}")
        services_status["openai"] = "error"

    # Overall status
    overall_status = "healthy" if all(
        s == "ok" for s in services_status.values()
    ) else "unhealthy"

    return {
        "status": overall_status,
        "services": services_status,
        "timestamp": datetime.utcnow().isoformat()
    }
