"""
SQLAlchemy models for conversation and message entities.

Uses Neon Serverless Postgres for storing chat history.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Conversation(Base):
    """
    Represents a user's chat session with the chatbot.

    Attributes:
        id: Unique conversation identifier (UUID)
        session_id: Browser-generated session UUID for tracking user sessions
        created_at: Timestamp when conversation was created
        updated_at: Timestamp when conversation was last updated
        messages: Relationship to Message entities
    """
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_conversations_session_id', 'session_id'),
        Index('ix_conversations_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id={self.session_id})>"

    def get_messages(self, limit: int = 50):
        """
        Get messages in this conversation.

        Args:
            limit: Maximum number of messages to return

        Returns:
            List of Message objects ordered by creation time
        """
        return sorted(self.messages, key=lambda m: m.created_at)[:limit]

    def get_recent_context(self, max_messages: int = 10):
        """
        Get recent conversation context as (role, content) tuples.

        Args:
            max_messages: Maximum number of recent messages

        Returns:
            List of (role, content) tuples
        """
        recent_messages = sorted(self.messages, key=lambda m: m.created_at)[-max_messages:]
        return [(msg.role, msg.content) for msg in recent_messages]

    def message_count(self) -> int:
        """Get total number of messages in conversation."""
        return len(self.messages)


class Message(Base):
    """
    Represents a single message in a conversation (user question or assistant response).

    Attributes:
        id: Unique message identifier (UUID)
        conversation_id: Foreign key to parent conversation
        role: Message role ('user' or 'assistant')
        content: Message text content
        cited_chunks: JSON array of ContentChunk UUIDs referenced in response (assistant only)
        selected_text: User-selected text context (user messages only, for P3 feature)
        created_at: Timestamp when message was created
        conversation: Relationship to parent Conversation
    """
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey('conversations.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    role = Column(SQLEnum('user', 'assistant', name='message_role'), nullable=False)
    content = Column(Text, nullable=False)
    cited_chunks = Column(JSON, nullable=True)  # Array of chunk UUIDs: ["uuid1", "uuid2"]
    selected_text = Column(Text, nullable=True)  # User-selected context (if P3 feature used)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    # Indexes
    __table_args__ = (
        Index('ix_messages_conversation_id', 'conversation_id'),
        Index('ix_messages_created_at', 'created_at'),
        Index('ix_messages_role', 'role'),
    )

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"

    def get_cited_chunk_ids(self):
        """
        Get list of cited chunk UUIDs.

        Returns:
            List of UUID strings
        """
        return self.cited_chunks or []

    def has_citations(self) -> bool:
        """Check if message has any citations."""
        return bool(self.cited_chunks)

    def citation_count(self) -> int:
        """Get number of citations in message."""
        return len(self.cited_chunks) if self.cited_chunks else 0