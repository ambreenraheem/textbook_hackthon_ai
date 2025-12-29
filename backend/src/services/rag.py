"""
RAG (Retrieval-Augmented Generation) pipeline orchestrator.

Orchestrates the RAG workflow:
1. Query → Retrieve relevant chunks
2. Format chunks as context for LLM
3. Include conversation history
4. Optimize token usage
"""
from typing import List, Dict, Optional, Tuple
from uuid import UUID

from src.services.retrieval import HybridRetriever, RetrievedChunk
from src.config.settings import get_settings
from src.utils.app_logging import get_logger

logger = get_logger(__name__)


class ConversationMessage:
    """
    Represents a message in conversation history.
    """

    def __init__(self, role: str, content: str):
        """
        Initialize conversation message.

        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        self.role = role
        self.content = content

    def to_dict(self) -> Dict:
        """Convert to OpenAI message format."""
        return {"role": self.role, "content": self.content}


class RAGPipeline:
    """
    RAG pipeline orchestrator for context-aware LLM responses.

    Features:
    - Retrieval of relevant textbook chunks
    - Context formatting with metadata
    - Conversation history management
    - Token budget optimization
    """

    def __init__(self, retriever: Optional[HybridRetriever] = None):
        """
        Initialize RAG pipeline.

        Args:
            retriever: Hybrid retriever (creates new if None)
        """
        if retriever is None:
            self.retriever = HybridRetriever()
        else:
            self.retriever = retriever

        settings = get_settings()
        self.rerank_top_n = settings.rerank_top_n
        self.logger = get_logger(__name__)

    def retrieve_context(
        self,
        query: str,
        selected_text: Optional[str] = None,
        chapter_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant context chunks for a query.

        Args:
            query: User's question
            selected_text: User-selected text for contextual search
            chapter_filter: Optional chapter filter
            section_filter: Optional section filter
            top_k: Number of chunks to retrieve (uses config default if None)

        Returns:
            List of retrieved chunks with metadata
        """
        if top_k is None:
            top_k = self.rerank_top_n

        # If user selected text, combine it with the query
        enhanced_query = query
        if selected_text:
            enhanced_query = f"{selected_text}\n\nQuestion: {query}"
            self.logger.info(f"Enhanced query with selected text ({len(selected_text)} chars)")

        # Retrieve chunks
        chunks = self.retriever.retrieve(
            query=enhanced_query,
            top_k=top_k,
            chapter_filter=chapter_filter,
            section_filter=section_filter,
            use_hybrid=True
        )

        self.logger.info(
            f"Retrieved {len(chunks)} context chunks",
            extra={
                "extra_fields": {
                    "num_chunks": len(chunks),
                    "query_length": len(query),
                    "has_selected_text": selected_text is not None
                }
            }
        )

        return chunks

    def format_context_for_llm(self, chunks: List[RetrievedChunk]) -> str:
        """
        Format retrieved chunks as context for LLM prompt.

        Each chunk includes:
        - Chunk number (for citation)
        - Content
        - Source metadata (chapter, section, page)

        Args:
            chunks: List of retrieved chunks

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant context found in the textbook."

        context_parts = []
        context_parts.append("=== TEXTBOOK CONTEXT ===\n")
        context_parts.append("The following excerpts from the Physical AI & Humanoid Robotics textbook are relevant to the user's question:\n")

        for idx, chunk in enumerate(chunks, start=1):
            context_parts.append(f"\n[Chunk {idx}]")
            context_parts.append(f"Source: {chunk.chapter} > {chunk.section}")
            if chunk.page:
                context_parts.append(f"Page: {chunk.page}")
            context_parts.append(f"Content: {chunk.content}")
            context_parts.append("")  # Blank line

        context_parts.append("=== END CONTEXT ===\n")

        context = "\n".join(context_parts)

        # Log token estimate (rough: 1 token ≈ 4 chars)
        estimated_tokens = len(context) // 4
        self.logger.info(
            f"Formatted context: ~{estimated_tokens} tokens from {len(chunks)} chunks"
        )

        return context

    def build_conversation_history(
        self,
        messages: List[Tuple[str, str]],
        max_history: int = 5
    ) -> List[ConversationMessage]:
        """
        Build conversation history for LLM context.

        Args:
            messages: List of (role, content) tuples
            max_history: Maximum number of recent messages to include

        Returns:
            List of ConversationMessage objects
        """
        # Take only recent messages to avoid token overflow
        recent_messages = messages[-max_history:] if len(messages) > max_history else messages

        conversation = []
        for role, content in recent_messages:
            conversation.append(ConversationMessage(role=role, content=content))

        self.logger.info(
            f"Built conversation history with {len(conversation)} messages "
            f"(total: {len(messages)}, max: {max_history})"
        )

        return conversation

    def create_system_prompt(self) -> str:
        """
        Create system prompt for the LLM.

        Returns:
            System prompt string
        """
        system_prompt = """You are an expert AI tutor for the Physical AI & Humanoid Robotics textbook. Your role is to help students understand complex robotics concepts by providing clear, accurate, and pedagogical explanations.

GUIDELINES:
1. Answer based PRIMARILY on the provided textbook context
2. If the context doesn't contain enough information, acknowledge the limitation and provide general guidance
3. Use analogies and examples to make concepts accessible
4. When referencing specific information, cite the chunk number (e.g., "[Chunk 1]")
5. Be concise but thorough - aim for clarity over verbosity
6. If asked about topics beyond the textbook scope, politely redirect to textbook content
7. Encourage deeper understanding by suggesting related topics when relevant

CITATION RULES:
- When you reference information from a specific chunk, cite it as [Chunk N]
- You can cite multiple chunks: [Chunk 1, Chunk 3]
- Citations help students find the source material in the textbook

TONE:
- Professional yet approachable
- Patient and encouraging
- Focused on student learning outcomes
"""
        return system_prompt

    def create_user_prompt(
        self,
        query: str,
        context: str,
        selected_text: Optional[str] = None
    ) -> str:
        """
        Create user prompt combining query and context.

        Args:
            query: User's question
            context: Formatted context from retrieval
            selected_text: Optional user-selected text

        Returns:
            Complete user prompt
        """
        prompt_parts = []

        # Add context
        prompt_parts.append(context)

        # Add selected text context if provided
        if selected_text:
            prompt_parts.append(f"\n=== USER-SELECTED TEXT ===")
            prompt_parts.append(f"{selected_text}")
            prompt_parts.append(f"=== END SELECTED TEXT ===\n")

        # Add user question
        prompt_parts.append(f"STUDENT QUESTION: {query}")

        return "\n".join(prompt_parts)

    def prepare_llm_messages(
        self,
        query: str,
        chunks: List[RetrievedChunk],
        conversation_history: Optional[List[Tuple[str, str]]] = None,
        selected_text: Optional[str] = None
    ) -> List[Dict]:
        """
        Prepare complete message list for LLM API call.

        Args:
            query: User's question
            chunks: Retrieved context chunks
            conversation_history: Optional conversation history as (role, content) tuples
            selected_text: Optional user-selected text

        Returns:
            List of message dictionaries in OpenAI format
        """
        messages = []

        # System prompt
        system_prompt = self.create_system_prompt()
        messages.append({"role": "system", "content": system_prompt})

        # Conversation history (if any)
        if conversation_history:
            history_messages = self.build_conversation_history(conversation_history)
            for msg in history_messages:
                messages.append(msg.to_dict())

        # Format context
        context = self.format_context_for_llm(chunks)

        # Create user prompt with context and query
        user_prompt = self.create_user_prompt(query, context, selected_text)
        messages.append({"role": "user", "content": user_prompt})

        # Log message stats
        total_chars = sum(len(m["content"]) for m in messages)
        estimated_tokens = total_chars // 4
        self.logger.info(
            f"Prepared LLM messages: {len(messages)} messages, ~{estimated_tokens} tokens",
            extra={
                "extra_fields": {
                    "num_messages": len(messages),
                    "estimated_tokens": estimated_tokens,
                    "has_history": conversation_history is not None,
                    "num_chunks": len(chunks)
                }
            }
        )

        return messages

    def optimize_context_for_token_budget(
        self,
        chunks: List[RetrievedChunk],
        max_tokens: int = 4000
    ) -> List[RetrievedChunk]:
        """
        Optimize context chunks to fit within token budget.

        Args:
            chunks: Retrieved chunks
            max_tokens: Maximum token budget for context

        Returns:
            Filtered chunks that fit within budget
        """
        # Rough estimate: 1 token ≈ 4 characters
        chars_per_token = 4
        max_chars = max_tokens * chars_per_token

        optimized_chunks = []
        total_chars = 0

        for chunk in chunks:
            # Estimate chunk size (content + metadata overhead)
            chunk_chars = len(chunk.content) + 200  # 200 chars for metadata

            if total_chars + chunk_chars <= max_chars:
                optimized_chunks.append(chunk)
                total_chars += chunk_chars
            else:
                # Token budget exceeded
                self.logger.warning(
                    f"Token budget exceeded: keeping {len(optimized_chunks)}/{len(chunks)} chunks"
                )
                break

        return optimized_chunks

    def process_query(
        self,
        query: str,
        selected_text: Optional[str] = None,
        conversation_history: Optional[List[Tuple[str, str]]] = None,
        chapter_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        optimize_tokens: bool = True
    ) -> Tuple[List[Dict], List[RetrievedChunk]]:
        """
        Complete RAG pipeline: retrieve context and prepare LLM messages.

        Args:
            query: User's question
            selected_text: Optional user-selected text
            conversation_history: Optional conversation history
            chapter_filter: Optional chapter filter
            section_filter: Optional section filter
            optimize_tokens: Whether to optimize context for token budget

        Returns:
            Tuple of (messages for LLM, retrieved chunks with metadata)
        """
        self.logger.info(
            f"Processing RAG query: {query[:100]}...",
            extra={"extra_fields": {"query_length": len(query)}}
        )

        # Step 1: Retrieve context
        chunks = self.retrieve_context(
            query=query,
            selected_text=selected_text,
            chapter_filter=chapter_filter,
            section_filter=section_filter
        )

        # Step 2: Optimize for token budget if needed
        if optimize_tokens:
            chunks = self.optimize_context_for_token_budget(chunks)

        # Step 3: Prepare LLM messages
        messages = self.prepare_llm_messages(
            query=query,
            chunks=chunks,
            conversation_history=conversation_history,
            selected_text=selected_text
        )

        self.logger.info(
            "RAG pipeline completed successfully",
            extra={
                "extra_fields": {
                    "num_chunks": len(chunks),
                    "num_messages": len(messages)
                }
            }
        )

        return messages, chunks
