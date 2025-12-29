"""
Tests for markdown parser module.
"""
import pytest
from pathlib import Path
from src.ingestion.parser import MarkdownParser, ParsedDocument, Section


def test_parser_initialization():
    """Test that parser initializes correctly."""
    parser = MarkdownParser()
    assert parser is not None


def test_extract_plain_text():
    """Test plain text extraction from markdown."""
    parser = MarkdownParser()

    markdown = """
    # Heading

    This is **bold** and *italic* text.

    Here's a [link](https://example.com).

    ```python
    print("code")
    ```

    And some `inline code`.
    """

    plain = parser.extract_plain_text(markdown)

    # Should remove formatting
    assert "**bold**" not in plain
    assert "*italic*" not in plain
    assert "bold" in plain
    assert "italic" in plain

    # Should remove code blocks
    assert "```" not in plain
    assert 'print("code")' not in plain

    # Should remove links but keep text
    assert "[link]" not in plain
    assert "link" in plain

    # Should remove inline code markers
    assert "`inline code`" not in plain
    assert "inline code" in plain


def test_extract_chapter_from_path():
    """Test chapter extraction from file path."""
    parser = MarkdownParser()

    # Test part and chapter
    path = Path("E:/docs/part-01-foundations/ch01-intro-physical-ai.mdx")
    chapter = parser._extract_chapter_from_path(path)
    assert "Part 1" in chapter
    assert "Foundations" in chapter
    assert "Chapter 1" in chapter

    # Test just part
    path = Path("E:/docs/part-02-ros2/intro.md")
    chapter = parser._extract_chapter_from_path(path)
    assert "Part 2" in chapter


def test_construct_url_path():
    """Test URL path construction."""
    parser = MarkdownParser()

    # Test with doc ID in metadata
    path = Path("E:/project/frontend/docs/part-01-foundations/ch01-intro.mdx")
    metadata = {"id": "ch01-intro-physical-ai"}
    url = parser._construct_url_path(path, metadata)
    assert "/docs/" in url
    assert "ch01-intro-physical-ai" in url

    # Test without doc ID
    metadata = {}
    url = parser._construct_url_path(path, metadata)
    assert "/docs/" in url


def test_extract_code_blocks():
    """Test code block extraction."""
    parser = MarkdownParser()

    content = """
Some text here.

```python
def hello():
    print("world")
```

More text.

```javascript
console.log("test");
```
"""

    code_blocks = parser._extract_code_blocks(content, 0)

    assert len(code_blocks) == 2
    assert code_blocks[0].language == "python"
    assert "def hello()" in code_blocks[0].content
    assert code_blocks[1].language == "javascript"
    assert "console.log" in code_blocks[1].content


def test_parse_sections():
    """Test section parsing."""
    parser = MarkdownParser()

    content = """
# Section 1

Content for section 1.

## Subsection 1.1

Content for subsection.

# Section 2

Content for section 2.
"""

    sections = parser._parse_sections(content)

    assert len(sections) >= 3

    # Check heading levels
    assert sections[0].level == 1
    assert sections[0].heading == "Section 1"

    assert sections[1].level == 2
    assert sections[1].heading == "Subsection 1.1"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
