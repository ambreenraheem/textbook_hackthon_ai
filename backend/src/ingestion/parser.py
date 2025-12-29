"""
Markdown/MDX parser for extracting structured content from textbook files.

Parses MDX files to extract headings, sections, code blocks, and metadata
while preserving markdown structure and handling MDX-specific components.
"""
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import frontmatter

from src.utils.app_logging import get_logger

logger = get_logger(__name__)


@dataclass
class CodeBlock:
    """Represents a code block with language and content."""
    language: str
    content: str
    line_start: int
    line_end: int


@dataclass
class Section:
    """Represents a section of content with heading and text."""
    heading: str
    level: int
    content: str
    line_start: int
    line_end: int
    code_blocks: List[CodeBlock]


@dataclass
class ParsedDocument:
    """Container for parsed markdown document with metadata."""
    file_path: str
    metadata: Dict
    sections: List[Section]
    title: str
    chapter: str
    description: str
    keywords: List[str]
    url_path: str


class MarkdownParser:
    """
    Parser for MDX textbook content.

    Extracts structured information from markdown files including:
    - Frontmatter metadata (YAML)
    - Headings and section hierarchy
    - Code blocks with syntax highlighting
    - MDX components (preserved as text)
    """

    # Regex patterns for markdown elements
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r'^```(\w+)?\n(.*?)^```$', re.MULTILINE | re.DOTALL)
    MDX_COMPONENT_PATTERN = re.compile(r'<(\w+)[^>]*>.*?</\1>|<(\w+)[^>]*/>', re.DOTALL)

    def __init__(self):
        """Initialize the markdown parser."""
        self.logger = get_logger(__name__)

    def parse_file(self, file_path: Path) -> ParsedDocument:
        """
        Parse a markdown/MDX file and extract structured content.

        Args:
            file_path: Path to the markdown file

        Returns:
            ParsedDocument containing metadata and sections

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file has invalid frontmatter or structure
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.logger.info(f"Parsing file: {file_path}")

        # Read file with frontmatter
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse frontmatter in {file_path}: {e}")

        metadata = post.metadata
        content = post.content

        # Extract metadata fields
        title = metadata.get('title', file_path.stem)
        chapter = self._extract_chapter_from_path(file_path)
        description = metadata.get('description', '')
        keywords = metadata.get('keywords', [])
        url_path = self._construct_url_path(file_path, metadata)

        # Parse sections
        sections = self._parse_sections(content)

        parsed_doc = ParsedDocument(
            file_path=str(file_path),
            metadata=metadata,
            sections=sections,
            title=title,
            chapter=chapter,
            description=description,
            keywords=keywords,
            url_path=url_path
        )

        self.logger.info(
            f"Parsed {len(sections)} sections from {file_path.name}"
        )

        return parsed_doc

    def _extract_chapter_from_path(self, file_path: Path) -> str:
        """
        Extract chapter identifier from file path.

        Args:
            file_path: Path to the file

        Returns:
            Chapter identifier (e.g., "Part I - Chapter 1")
        """
        parts = file_path.parts

        # Find part directory (e.g., part-01-foundations)
        part_dir = None
        for part in parts:
            if part.startswith('part-'):
                part_dir = part
                break

        if part_dir:
            # Convert part-01-foundations to "Part 1: Foundations"
            part_match = re.match(r'part-(\d+)-(.+)', part_dir)
            if part_match:
                part_num = int(part_match.group(1))
                part_name = part_match.group(2).replace('-', ' ').title()

                # Extract chapter number from filename
                filename = file_path.stem
                ch_match = re.match(r'ch(\d+)-', filename)
                if ch_match:
                    ch_num = int(ch_match.group(1))
                    return f"Part {part_num}: {part_name} - Chapter {ch_num}"

                return f"Part {part_num}: {part_name}"

        return file_path.stem

    def _construct_url_path(self, file_path: Path, metadata: Dict) -> str:
        """
        Construct Docusaurus URL path from file path.

        Args:
            file_path: Path to the file
            metadata: Frontmatter metadata

        Returns:
            URL path for Docusaurus routing
        """
        # Use 'id' from frontmatter if available
        doc_id = metadata.get('id')

        parts = file_path.parts

        # Find docs directory index
        try:
            docs_idx = parts.index('docs')
        except ValueError:
            # If 'docs' not in path, use filename
            return f"/docs/{file_path.stem}"

        # Build path from docs directory
        path_parts = parts[docs_idx + 1:]

        # Remove .md/.mdx extension
        path_parts = list(path_parts[:-1]) + [path_parts[-1].replace('.mdx', '').replace('.md', '')]

        # Use doc_id if available, otherwise use full path
        if doc_id:
            # Construct path with doc_id
            if len(path_parts) > 1:
                return f"/docs/{'/'.join(path_parts[:-1])}/{doc_id}"
            else:
                return f"/docs/{doc_id}"

        return f"/docs/{'/'.join(path_parts)}"

    def _parse_sections(self, content: str) -> List[Section]:
        """
        Parse content into sections based on headings.

        Args:
            content: Markdown content string

        Returns:
            List of Section objects
        """
        lines = content.split('\n')
        sections = []

        # Find all headings
        headings = []
        for i, line in enumerate(lines):
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                headings.append((i, level, title))

        # Create sections between headings
        for i, (line_num, level, title) in enumerate(headings):
            # Determine section end
            if i < len(headings) - 1:
                end_line = headings[i + 1][0]
            else:
                end_line = len(lines)

            # Extract section content (excluding the heading line itself)
            section_content_lines = lines[line_num + 1:end_line]
            section_content = '\n'.join(section_content_lines).strip()

            # Extract code blocks in this section
            code_blocks = self._extract_code_blocks(section_content, line_num + 1)

            section = Section(
                heading=title,
                level=level,
                content=section_content,
                line_start=line_num,
                line_end=end_line,
                code_blocks=code_blocks
            )
            sections.append(section)

        # If no headings found, treat entire content as one section
        if not sections:
            code_blocks = self._extract_code_blocks(content, 0)
            sections.append(Section(
                heading="Introduction",
                level=1,
                content=content.strip(),
                line_start=0,
                line_end=len(lines),
                code_blocks=code_blocks
            ))

        return sections

    def _extract_code_blocks(self, content: str, offset: int) -> List[CodeBlock]:
        """
        Extract code blocks from content.

        Args:
            content: Content string to search
            offset: Line number offset for absolute positioning

        Returns:
            List of CodeBlock objects
        """
        code_blocks = []

        # Find all code blocks
        for match in self.CODE_BLOCK_PATTERN.finditer(content):
            language = match.group(1) or 'text'
            code_content = match.group(2).strip()

            # Calculate line positions
            pre_content = content[:match.start()]
            line_start = offset + pre_content.count('\n')
            line_end = line_start + code_content.count('\n') + 1

            code_blocks.append(CodeBlock(
                language=language,
                content=code_content,
                line_start=line_start,
                line_end=line_end
            ))

        return code_blocks

    def extract_plain_text(self, content: str) -> str:
        """
        Extract plain text from markdown content.

        Removes:
        - Code blocks
        - MDX components
        - Markdown formatting (bold, italic, links)
        - HTML tags

        Args:
            content: Markdown content

        Returns:
            Plain text content
        """
        # Remove code blocks
        text = self.CODE_BLOCK_PATTERN.sub('', content)

        # Remove MDX components
        text = self.MDX_COMPONENT_PATTERN.sub('', text)

        # Remove images
        text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)

        # Remove links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Remove bold/italic
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)

        # Remove inline code
        text = re.sub(r'`([^`]+)`', r'\1', text)

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Remove markdown headings markers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        # Remove horizontal rules
        text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)

        # Normalize whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)

        return text.strip()

    def parse_directory(self, directory: Path, pattern: str = "**/*.mdx") -> List[ParsedDocument]:
        """
        Parse all markdown files in a directory.

        Args:
            directory: Directory to search
            pattern: Glob pattern for files (default: **/*.mdx)

        Returns:
            List of ParsedDocument objects
        """
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        documents = []
        files = list(directory.glob(pattern))

        # Also include .md files
        if pattern == "**/*.mdx":
            files.extend(directory.glob("**/*.md"))

        self.logger.info(f"Found {len(files)} markdown files in {directory}")

        for file_path in files:
            # Skip files that don't look like content (e.g., _category_.json)
            if file_path.name.startswith('_') or file_path.suffix not in ['.md', '.mdx']:
                continue

            try:
                doc = self.parse_file(file_path)
                documents.append(doc)
            except Exception as e:
                self.logger.error(f"Failed to parse {file_path}: {e}")
                continue

        self.logger.info(f"Successfully parsed {len(documents)} documents")
        return documents
