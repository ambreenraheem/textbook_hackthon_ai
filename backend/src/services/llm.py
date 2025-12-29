"""
Streaming LLM service with Server-Sent Events (SSE) and citation extraction.

Features:
- Streaming responses using OpenAI GPT-4 Turbo
- Citation extraction from LLM responses
- Server-Sent Events (SSE) for real-time streaming
- Error handling and timeout management
"""
import re
import asyncio
from typing import List, Dict, Optional, AsyncGenerator
from uuid import UUID

from openai import AsyncOpenAI, OpenAIError, APITimeoutError, RateLimitError

from src.services.retrieval import RetrievedChunk
from src.config.settings import get_settings
from src.utils.app_logging import get_logger

logger = get_logger(__name__)


class CitationExtractor:
    """
    Extract citations from LLM responses.

    Identifies references to chunks (e.g., "[Chunk 1]", "[Chunk 2, 3]")
    and maps them to source metadata.
    """

    def __init__(self):
        # Pattern to match [Chunk N] or [Chunk N, M, ...]
        self.citation_pattern = re.compile(r'\[Chunk\s+(\d+(?:\s*,\s*\d+)*)\]', re.IGNORECASE)
        self.logger = get_logger(__name__)

    def extract_citations(self, text: str) -> List[int]:
        """
        Extract chunk numbers from citation references in text.

        Args:
            text: Text containing citation references

        Returns:
            List of unique chunk numbers (1-indexed)
        """
        citations = []
        matches = self.citation_pattern.finditer(text)

        for match in matches:
            # Extract comma-separated numbers
            numbers_str = match.group(1)
            numbers = [int(n.strip()) for n in numbers_str.split(',')]
            citations.extend(numbers)

        # Remove duplicates and sort
        unique_citations = sorted(set(citations))

        if unique_citations:
            self.logger.debug(f"Extracted citations: {unique_citations}")

        return unique_citations

    def map_citations_to_chunks(
        self,
        text: str,
        chunks: List[RetrievedChunk]
    ) -> List[RetrievedChunk]:
        """
        Map citation references to actual chunk metadata.

        Args:
            text: Text containing citations
            chunks: List of retrieved chunks (indexed from 1)

        Returns:
            List of cited chunks
        """
        citation_numbers = self.extract_citations(text)
        cited_chunks = []

        for num in citation_numbers:
            # Convert 1-indexed to 0-indexed
            idx = num - 1
            if 0 <= idx < len(chunks):
                cited_chunks.append(chunks[idx])
            else:
                self.logger.warning(f"Citation [Chunk {num}] out of range (max: {len(chunks)})")

        return cited_chunks


class StreamingLLM:
    """
    Streaming LLM service for RAG-powered responses.

    Handles:
    - Async streaming from OpenAI
    - Real-time token generation
    - Citation extraction and emission
    - Error handling and retries
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize streaming LLM service.

        Args:
            api_key: OpenAI API key (uses config default if None)
        """
        settings = get_settings()

        if api_key is None:
            api_key = settings.openai_api_key

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = settings.llm_model
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature
        self.citation_extractor = CitationExtractor()
        self.logger = get_logger(__name__)

    async def stream_response(
        self,
        messages: List[Dict],
        chunks: List[RetrievedChunk],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Stream LLM response with citations as Server-Sent Events.

        Yields events in order:
        1. 'token' events for each token
        2. 'citation' events for each cited chunk (after completion)
        3. 'done' event with conversation/message IDs (handled by caller)

        Args:
            messages: List of messages in OpenAI format
            chunks: Retrieved chunks for citation mapping
            temperature: LLM temperature (uses config default if None)
            max_tokens: Max tokens to generate (uses config default if None)

        Yields:
            Event dictionaries with 'type' and 'data' fields
        """
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens

        accumulated_response = ""

        try:
            self.logger.info(
                f"Starting LLM streaming with {self.model}",
                extra={
                    "extra_fields": {
                        "model": self.model,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "num_messages": len(messages)
                    }
                }
            )

            # Create streaming completion
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            # Stream tokens
            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta

                    if delta.content:
                        token = delta.content
                        accumulated_response += token

                        # Yield token event
                        yield {
                            "type": "token",
                            "data": {"token": token}
                        }

            # After streaming completes, extract citations
            self.logger.info(
                f"LLM streaming completed ({len(accumulated_response)} chars)"
            )

            # Extract and emit citation events
            cited_chunks = self.citation_extractor.map_citations_to_chunks(
                accumulated_response,
                chunks
            )

            self.logger.info(f"Extracted {len(cited_chunks)} citations")

            for chunk in cited_chunks:
                yield {
                    "type": "citation",
                    "data": {
                        "chunk_id": str(chunk.chunk_id),
                        "chapter": chunk.chapter,
                        "section": chunk.section,
                        "url": chunk.url
                    }
                }

            # Store complete response and cited chunks for later use
            self._last_response = accumulated_response
            self._last_cited_chunks = cited_chunks

        except RateLimitError as e:
            self.logger.error(f"OpenAI rate limit exceeded: {e}")
            yield {
                "type": "error",
                "data": {
                    "error": "RateLimitError",
                    "message": "API rate limit exceeded. Please try again in a moment."
                }
            }
            raise

        except APITimeoutError as e:
            self.logger.error(f"OpenAI API timeout: {e}")
            yield {
                "type": "error",
                "data": {
                    "error": "TimeoutError",
                    "message": "Request timed out. Please try again."
                }
            }
            raise

        except OpenAIError as e:
            self.logger.error(f"OpenAI API error: {e}", exc_info=True)
            yield {
                "type": "error",
                "data": {
                    "error": "OpenAIError",
                    "message": "An error occurred while generating the response. Please try again."
                }
            }
            raise

        except Exception as e:
            self.logger.error(f"Unexpected error during streaming: {e}", exc_info=True)
            yield {
                "type": "error",
                "data": {
                    "error": "InternalError",
                    "message": "An unexpected error occurred. Please try again."
                }
            }
            raise

    def get_last_response(self) -> Optional[str]:
        """
        Get the last complete response (for persistence).

        Returns:
            Complete response text or None
        """
        return getattr(self, '_last_response', None)

    def get_last_cited_chunks(self) -> List[RetrievedChunk]:
        """
        Get the last cited chunks (for persistence).

        Returns:
            List of cited chunks
        """
        return getattr(self, '_last_cited_chunks', [])

    async def generate_response(
        self,
        messages: List[Dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a complete (non-streaming) response.

        Useful for testing or non-streaming use cases.

        Args:
            messages: List of messages in OpenAI format
            temperature: LLM temperature (uses config default if None)
            max_tokens: Max tokens to generate (uses config default if None)

        Returns:
            Complete response text
        """
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens

        try:
            self.logger.info(f"Generating non-streaming response with {self.model}")

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            content = response.choices[0].message.content

            self.logger.info(
                f"Generated response ({len(content)} chars)",
                extra={
                    "extra_fields": {
                        "model": self.model,
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
            )

            return content

        except Exception as e:
            self.logger.error(f"Error generating response: {e}", exc_info=True)
            raise


class SSEFormatter:
    """
    Format events as Server-Sent Events (SSE) strings.

    SSE format:
    event: <event_type>
    data: <json_data>

    """

    @staticmethod
    def format_event(event_type: str, data: Dict) -> str:
        """
        Format event as SSE string.

        Args:
            event_type: Event type (token, citation, done, error)
            data: Event data dictionary

        Returns:
            SSE-formatted string
        """
        import json

        # Convert data to JSON
        data_json = json.dumps(data)

        # Format as SSE
        sse = f"event: {event_type}\ndata: {data_json}\n\n"

        return sse

    @staticmethod
    def format_token(token: str) -> str:
        """Format token event."""
        return SSEFormatter.format_event("token", {"token": token})

    @staticmethod
    def format_citation(chunk_id: str, chapter: str, section: str, url: str) -> str:
        """Format citation event."""
        return SSEFormatter.format_event(
            "citation",
            {
                "chunk_id": chunk_id,
                "chapter": chapter,
                "section": section,
                "url": url
            }
        )

    @staticmethod
    def format_done(conversation_id: str, message_id: str) -> str:
        """Format done event."""
        return SSEFormatter.format_event(
            "done",
            {
                "conversation_id": conversation_id,
                "message_id": message_id
            }
        )

    @staticmethod
    def format_error(error: str, message: str) -> str:
        """Format error event."""
        return SSEFormatter.format_event(
            "error",
            {
                "error": error,
                "message": message
            }
        )
