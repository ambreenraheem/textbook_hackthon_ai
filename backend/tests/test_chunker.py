"""
Tests for semantic chunker module.
"""
import pytest
from src.ingestion.chunker import SemanticChunker, ContentChunk
from src.ingestion.parser import ParsedDocument, Section


def test_chunker_initialization():
    """Test that chunker initializes correctly."""
    chunker = SemanticChunker()
    assert chunker is not None
    assert chunker.min_chunk_size == 400
    assert chunker.max_chunk_size == 600
    assert chunker.overlap_size == 50


def test_count_tokens():
    """Test token counting."""
    chunker = SemanticChunker()

    text = "This is a test sentence."
    token_count = chunker.count_tokens(text)

    # Should return a positive integer
    assert isinstance(token_count, int)
    assert token_count > 0


def test_split_into_paragraphs():
    """Test paragraph splitting."""
    chunker = SemanticChunker()

    text = """
First paragraph here.

Second paragraph here.


Third paragraph with extra space.
"""

    paragraphs = chunker._split_into_paragraphs(text)

    assert len(paragraphs) == 3
    assert "First paragraph" in paragraphs[0]
    assert "Second paragraph" in paragraphs[1]
    assert "Third paragraph" in paragraphs[2]


def test_update_heading_stack():
    """Test heading stack updates."""
    chunker = SemanticChunker()

    # Start with empty stack
    stack = []

    # Add level 1 heading
    section = Section(
        heading="Chapter 1",
        level=1,
        content="Content",
        line_start=0,
        line_end=10,
        code_blocks=[]
    )
    stack = chunker._update_heading_stack(stack, section)
    assert len(stack) == 1
    assert stack[0][1] == "Chapter 1"

    # Add level 2 heading (child)
    section = Section(
        heading="Section 1.1",
        level=2,
        content="Content",
        line_start=10,
        line_end=20,
        code_blocks=[]
    )
    stack = chunker._update_heading_stack(stack, section)
    assert len(stack) == 2
    assert stack[1][1] == "Section 1.1"

    # Add another level 1 heading (should pop level 2)
    section = Section(
        heading="Chapter 2",
        level=1,
        content="Content",
        line_start=20,
        line_end=30,
        code_blocks=[]
    )
    stack = chunker._update_heading_stack(stack, section)
    assert len(stack) == 1
    assert stack[0][1] == "Chapter 2"


def test_create_chunk():
    """Test chunk creation with metadata."""
    chunker = SemanticChunker()

    # Create mock document
    document = ParsedDocument(
        file_path="/path/to/file.mdx",
        metadata={},
        sections=[],
        title="Test Document",
        chapter="Chapter 1",
        description="Test description",
        keywords=["test", "demo"],
        url_path="/docs/test"
    )

    # Create mock section
    section = Section(
        heading="Test Section",
        level=1,
        content="Test content",
        line_start=0,
        line_end=10,
        code_blocks=[]
    )

    # Create chunk
    chunk = chunker._create_chunk(
        text="This is a test chunk.",
        heading_path=["Chapter 1", "Test Section"],
        document=document,
        section=section,
        chunk_index=0
    )

    assert isinstance(chunk, ContentChunk)
    assert chunk.text == "This is a test chunk."
    assert chunk.metadata['chapter'] == "Chapter 1"
    assert chunk.metadata['section'] == "Test Section"
    assert chunk.metadata['title'] == "Test Document"
    assert chunk.token_count > 0


def test_get_overlap_text():
    """Test overlap text extraction."""
    chunker = SemanticChunker(overlap_size=10)

    text = "This is a long sentence that should be used for testing overlap extraction."
    overlap = chunker._get_overlap_text(text)

    # Should return end of text
    assert isinstance(overlap, str)
    assert len(overlap) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
