"""
Semantic chunker for splitting textbook content into optimal-sized chunks.

Creates chunks of 400-600 tokens that respect heading boundaries and include
metadata for context preservation and retrieval.
"""
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import tiktoken

from src.ingestion.parser import ParsedDocument, Section
from src.utils.app_logging import get_logger

logger = get_logger(__name__)


@dataclass
class ContentChunk:
    """
    Represents a chunk of content ready for embedding.

    Attributes:
        text: The chunk text content
        metadata: Associated metadata (chapter, section, url, etc.)
        token_count: Number of tokens in the chunk
        heading_path: Hierarchical path of headings (e.g., ["Chapter 1", "Section 1.1"])
        source_file: Original source file path
        line_start: Starting line in source file
        line_end: Ending line in source file
    """
    text: str
    metadata: Dict
    token_count: int
    heading_path: List[str]
    source_file: str
    line_start: int
    line_end: int


class SemanticChunker:
    """
    Semantic chunker that splits content into optimal-sized chunks.

    Features:
    - Respects heading boundaries (doesn't split mid-section)
    - Target chunk size: 400-600 tokens
    - Includes overlap for context preservation
    - Preserves metadata for retrieval
    """

    def __init__(
        self,
        min_chunk_size: int = 400,
        max_chunk_size: int = 600,
        overlap_size: int = 50,
        encoding_name: str = "cl100k_base"  # Used by text-embedding-3-small
    ):
        """
        Initialize the semantic chunker.

        Args:
            min_chunk_size: Minimum tokens per chunk
            max_chunk_size: Maximum tokens per chunk
            overlap_size: Number of overlapping tokens between chunks
            encoding_name: Tokenizer encoding name (cl100k_base for OpenAI embeddings)
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size

        # Initialize tokenizer
        try:
            self.tokenizer = tiktoken.get_encoding(encoding_name)
        except Exception as e:
            logger.warning(f"Failed to load tokenizer {encoding_name}, using default: {e}")
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

        self.logger = get_logger(__name__)

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using the configured tokenizer.

        Args:
            text: Text to tokenize

        Returns:
            Number of tokens
        """
        return len(self.tokenizer.encode(text))

    def chunk_document(self, document: ParsedDocument) -> List[ContentChunk]:
        """
        Chunk a parsed document into semantic chunks.

        Args:
            document: ParsedDocument to chunk

        Returns:
            List of ContentChunk objects
        """
        chunks = []
        heading_stack = []  # Track heading hierarchy

        self.logger.info(
            f"Chunking document: {document.title} ({len(document.sections)} sections)"
        )

        for section in document.sections:
            # Update heading stack based on section level
            heading_stack = self._update_heading_stack(heading_stack, section)

            # Create chunks for this section
            section_chunks = self._chunk_section(
                section=section,
                heading_path=heading_stack.copy(),
                document=document
            )

            chunks.extend(section_chunks)

        self.logger.info(
            f"Created {len(chunks)} chunks from document {document.title}"
        )

        return chunks

    def _update_heading_stack(
        self,
        heading_stack: List[tuple],
        section: Section
    ) -> List[tuple]:
        """
        Update the heading hierarchy stack.

        Args:
            heading_stack: Current stack of (level, heading) tuples
            section: New section being processed

        Returns:
            Updated heading stack
        """
        # Remove headings at same or deeper level
        while heading_stack and heading_stack[-1][0] >= section.level:
            heading_stack.pop()

        # Add current heading
        heading_stack.append((section.level, section.heading))

        return heading_stack

    def _chunk_section(
        self,
        section: Section,
        heading_path: List[tuple],
        document: ParsedDocument
    ) -> List[ContentChunk]:
        """
        Create chunks from a section.

        Args:
            section: Section to chunk
            heading_path: Hierarchical heading path
            document: Parent document

        Returns:
            List of ContentChunk objects
        """
        chunks = []

        # Get plain heading path (just strings)
        heading_strings = [h[1] for h in heading_path]

        # Count tokens in section
        section_tokens = self.count_tokens(section.content)

        # If section fits in one chunk, create single chunk
        if section_tokens <= self.max_chunk_size:
            chunk = self._create_chunk(
                text=section.content,
                heading_path=heading_strings,
                document=document,
                section=section,
                chunk_index=0
            )
            chunks.append(chunk)
        else:
            # Split large section into multiple chunks
            section_chunks = self._split_large_section(
                section=section,
                heading_path=heading_strings,
                document=document
            )
            chunks.extend(section_chunks)

        return chunks

    def _split_large_section(
        self,
        section: Section,
        heading_path: List[str],
        document: ParsedDocument
    ) -> List[ContentChunk]:
        """
        Split a large section into multiple chunks.

        Uses paragraph boundaries and tries to create chunks of optimal size
        with overlap for context preservation.

        Args:
            section: Section to split
            heading_path: Hierarchical heading path
            document: Parent document

        Returns:
            List of ContentChunk objects
        """
        chunks = []

        # Split content into paragraphs
        paragraphs = self._split_into_paragraphs(section.content)

        current_chunk_text = ""
        current_tokens = 0
        chunk_index = 0

        for para in paragraphs:
            para_tokens = self.count_tokens(para)

            # If adding this paragraph would exceed max size
            if current_tokens + para_tokens > self.max_chunk_size:
                # Save current chunk if it meets minimum size
                if current_tokens >= self.min_chunk_size:
                    chunk = self._create_chunk(
                        text=current_chunk_text.strip(),
                        heading_path=heading_path,
                        document=document,
                        section=section,
                        chunk_index=chunk_index
                    )
                    chunks.append(chunk)
                    chunk_index += 1

                    # Start new chunk with overlap
                    current_chunk_text = self._get_overlap_text(current_chunk_text) + "\n\n" + para
                    current_tokens = self.count_tokens(current_chunk_text)
                else:
                    # Current chunk too small, just add paragraph
                    current_chunk_text += "\n\n" + para
                    current_tokens += para_tokens
            else:
                # Add paragraph to current chunk
                if current_chunk_text:
                    current_chunk_text += "\n\n" + para
                else:
                    current_chunk_text = para
                current_tokens += para_tokens

        # Save final chunk
        if current_chunk_text.strip():
            chunk = self._create_chunk(
                text=current_chunk_text.strip(),
                heading_path=heading_path,
                document=document,
                section=section,
                chunk_index=chunk_index
            )
            chunks.append(chunk)

        return chunks

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs.

        Args:
            text: Text to split

        Returns:
            List of paragraph strings
        """
        # Split on double newlines
        paragraphs = re.split(r'\n\s*\n', text)

        # Filter out empty paragraphs
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        return paragraphs

    def _get_overlap_text(self, text: str) -> str:
        """
        Get overlap text from the end of current chunk.

        Args:
            text: Current chunk text

        Returns:
            Overlap text (last ~overlap_size tokens)
        """
        tokens = self.tokenizer.encode(text)

        if len(tokens) <= self.overlap_size:
            return text

        # Get last overlap_size tokens
        overlap_tokens = tokens[-self.overlap_size:]
        overlap_text = self.tokenizer.decode(overlap_tokens)

        return overlap_text

    def _create_chunk(
        self,
        text: str,
        heading_path: List[str],
        document: ParsedDocument,
        section: Section,
        chunk_index: int
    ) -> ContentChunk:
        """
        Create a ContentChunk with metadata.

        Args:
            text: Chunk text
            heading_path: Hierarchical heading path
            document: Parent document
            section: Source section
            chunk_index: Index of chunk within section

        Returns:
            ContentChunk object
        """
        token_count = self.count_tokens(text)

        # Build metadata
        metadata = {
            'chapter': document.chapter,
            'title': document.title,
            'section': section.heading,
            'heading_path': ' > '.join(heading_path),
            'url': document.url_path,
            'description': document.description,
            'keywords': document.keywords,
            'chunk_index': chunk_index,
            'source_file': document.file_path,
            'line_start': section.line_start,
            'line_end': section.line_end
        }

        return ContentChunk(
            text=text,
            metadata=metadata,
            token_count=token_count,
            heading_path=heading_path,
            source_file=document.file_path,
            line_start=section.line_start,
            line_end=section.line_end
        )

    def chunk_documents(self, documents: List[ParsedDocument]) -> List[ContentChunk]:
        """
        Chunk multiple documents.

        Args:
            documents: List of ParsedDocument objects

        Returns:
            List of all ContentChunk objects
        """
        all_chunks = []

        for doc in documents:
            try:
                chunks = self.chunk_document(doc)
                all_chunks.extend(chunks)
            except Exception as e:
                self.logger.error(f"Failed to chunk document {doc.file_path}: {e}")
                continue

        self.logger.info(
            f"Chunked {len(documents)} documents into {len(all_chunks)} chunks"
        )

        # Log statistics
        if all_chunks:
            token_counts = [c.token_count for c in all_chunks]
            avg_tokens = sum(token_counts) / len(token_counts)
            min_tokens = min(token_counts)
            max_tokens = max(token_counts)

            self.logger.info(
                f"Chunk statistics - Avg: {avg_tokens:.0f}, Min: {min_tokens}, Max: {max_tokens}"
            )

        return all_chunks
