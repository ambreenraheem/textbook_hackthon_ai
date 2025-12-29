"""
RAG Pipeline Test Script

Tests the complete RAG pipeline end-to-end without making actual API calls.
Useful for validating the implementation before deployment.

Usage:
    python backend/test_rag_pipeline.py
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.retrieval import RetrievedChunk, BM25, HybridRetriever
from src.services.rag import RAGPipeline, ConversationMessage
from src.services.llm import CitationExtractor, SSEFormatter
from src.utils.app_logging import setup_logging, get_logger
import uuid

# Setup logging
setup_logging()
logger = get_logger(__name__)


def test_retrieved_chunk():
    """Test RetrievedChunk data class."""
    print("\n=== Testing RetrievedChunk ===")

    chunk = RetrievedChunk(
        chunk_id=uuid.uuid4(),
        content="Forward kinematics involves calculating the position...",
        score=0.85,
        chapter="Robot Kinematics",
        section="2.1 Forward Kinematics",
        page=42,
        url="/chapters/02-kinematics#forward-kinematics",
        metadata={"type": "textbook"}
    )

    print(f"Chunk: {chunk}")
    print(f"Dict: {chunk.to_dict()}")

    assert chunk.score == 0.85
    assert chunk.chapter == "Robot Kinematics"
    print("[PASS] RetrievedChunk test passed")


def test_bm25():
    """Test BM25 implementation."""
    print("\n=== Testing BM25 ===")

    bm25 = BM25()

    # Test tokenization
    tokens = bm25.tokenize("What is inverse kinematics?")
    print(f"Tokens: {tokens}")
    assert "inverse" in tokens
    assert "kinematics" in tokens

    # Test scoring
    documents = [
        (uuid.uuid4(), "Inverse kinematics is a method for calculating joint angles."),
        (uuid.uuid4(), "Forward kinematics calculates end-effector position."),
        (uuid.uuid4(), "The inverse kinematics problem is more complex than forward kinematics.")
    ]

    scores = bm25.score_documents("inverse kinematics", documents)
    print(f"BM25 Scores:")
    for doc_id, score in scores[:3]:
        print(f"  {score:.4f}")

    # First document should have highest score (contains both terms)
    assert scores[0][1] > scores[1][1]
    print("[PASS] BM25 test passed")


def test_citation_extractor():
    """Test citation extraction."""
    print("\n=== Testing CitationExtractor ===")

    extractor = CitationExtractor()

    # Test single citation
    text = "Forward kinematics is explained in [Chunk 1]."
    citations = extractor.extract_citations(text)
    print(f"Citations from '{text}': {citations}")
    assert citations == [1]

    # Test multiple citations
    text = "See [Chunk 1] and [Chunk 3] for details."
    citations = extractor.extract_citations(text)
    print(f"Citations from '{text}': {citations}")
    assert set(citations) == {1, 3}

    # Test comma-separated citations
    text = "Refer to [Chunk 1, 2, 3] for more information."
    citations = extractor.extract_citations(text)
    print(f"Citations from '{text}': {citations}")
    assert set(citations) == {1, 2, 3}

    # Test no citations
    text = "This text has no citations."
    citations = extractor.extract_citations(text)
    print(f"Citations from '{text}': {citations}")
    assert citations == []

    # Test mapping to chunks
    chunks = [
        RetrievedChunk(
            chunk_id=uuid.uuid4(),
            content="Content 1",
            score=0.9,
            chapter="Chapter 1",
            section="Section 1",
            page=1,
            url="/ch1"
        ),
        RetrievedChunk(
            chunk_id=uuid.uuid4(),
            content="Content 2",
            score=0.8,
            chapter="Chapter 2",
            section="Section 2",
            page=2,
            url="/ch2"
        )
    ]

    text = "See [Chunk 1] and [Chunk 2]."
    cited_chunks = extractor.map_citations_to_chunks(text, chunks)
    print(f"Cited chunks: {len(cited_chunks)}")
    assert len(cited_chunks) == 2

    print("[PASS] CitationExtractor test passed")


def test_sse_formatter():
    """Test SSE formatting."""
    print("\n=== Testing SSEFormatter ===")

    # Test token event
    sse = SSEFormatter.format_token("Hello")
    print(f"Token SSE:\n{sse}")
    assert "event: token" in sse
    assert '"token": "Hello"' in sse

    # Test citation event
    sse = SSEFormatter.format_citation(
        chunk_id="uuid-here",
        chapter="Robot Kinematics",
        section="2.1 Forward Kinematics",
        url="/chapters/02-kinematics"
    )
    print(f"Citation SSE:\n{sse}")
    assert "event: citation" in sse
    assert "Robot Kinematics" in sse

    # Test done event
    sse = SSEFormatter.format_done(
        conversation_id="conv-uuid",
        message_id="msg-uuid"
    )
    print(f"Done SSE:\n{sse}")
    assert "event: done" in sse
    assert "conv-uuid" in sse

    # Test error event
    sse = SSEFormatter.format_error(
        error="TestError",
        message="This is a test error"
    )
    print(f"Error SSE:\n{sse}")
    assert "event: error" in sse
    assert "TestError" in sse

    print("[PASS] SSEFormatter test passed")


def test_conversation_message():
    """Test ConversationMessage."""
    print("\n=== Testing ConversationMessage ===")

    msg = ConversationMessage(role="user", content="What is a robot?")
    print(f"Message: {msg.to_dict()}")

    assert msg.role == "user"
    assert msg.content == "What is a robot?"

    msg_dict = msg.to_dict()
    assert msg_dict["role"] == "user"
    assert msg_dict["content"] == "What is a robot?"

    print("[PASS] ConversationMessage test passed")


def test_rag_pipeline_context_formatting():
    """Test RAG pipeline context formatting."""
    print("\n=== Testing RAG Pipeline Context Formatting ===")

    pipeline = RAGPipeline()

    # Create mock chunks
    chunks = [
        RetrievedChunk(
            chunk_id=uuid.uuid4(),
            content="Forward kinematics calculates the end-effector position.",
            score=0.9,
            chapter="Robot Kinematics",
            section="2.1 Forward Kinematics",
            page=42,
            url="/chapters/02-kinematics#forward"
        ),
        RetrievedChunk(
            chunk_id=uuid.uuid4(),
            content="Inverse kinematics solves for joint angles.",
            score=0.85,
            chapter="Robot Kinematics",
            section="2.3 Inverse Kinematics",
            page=45,
            url="/chapters/02-kinematics#inverse"
        )
    ]

    # Test context formatting
    context = pipeline.format_context_for_llm(chunks)
    print(f"Formatted context:\n{context}")

    assert "[Chunk 1]" in context
    assert "[Chunk 2]" in context
    assert "Robot Kinematics" in context
    assert "Forward kinematics" in context

    print("[PASS] RAG Pipeline context formatting test passed")


def test_rag_pipeline_system_prompt():
    """Test RAG pipeline system prompt."""
    print("\n=== Testing RAG Pipeline System Prompt ===")

    pipeline = RAGPipeline()
    system_prompt = pipeline.create_system_prompt()

    print(f"System prompt length: {len(system_prompt)} chars")
    print(f"System prompt preview:\n{system_prompt[:200]}...")

    assert "Physical AI" in system_prompt
    assert "Robotics" in system_prompt
    assert "citation" in system_prompt.lower()

    print("[PASS] RAG Pipeline system prompt test passed")


def test_rag_pipeline_user_prompt():
    """Test RAG pipeline user prompt creation."""
    print("\n=== Testing RAG Pipeline User Prompt ===")

    pipeline = RAGPipeline()

    context = "=== TEXTBOOK CONTEXT ===\n[Chunk 1] Forward kinematics..."
    query = "What is forward kinematics?"

    # Without selected text
    user_prompt = pipeline.create_user_prompt(query, context, selected_text=None)
    print(f"User prompt (no selection):\n{user_prompt[:200]}...")

    assert context in user_prompt
    assert query in user_prompt

    # With selected text
    selected_text = "The Denavit-Hartenberg convention is used..."
    user_prompt = pipeline.create_user_prompt(query, context, selected_text)
    print(f"User prompt (with selection):\n{user_prompt[:200]}...")

    assert context in user_prompt
    assert query in user_prompt
    assert selected_text in user_prompt

    print("[PASS] RAG Pipeline user prompt test passed")


def test_rag_pipeline_conversation_history():
    """Test conversation history building."""
    print("\n=== Testing Conversation History ===")

    pipeline = RAGPipeline()

    messages = [
        ("user", "What is a robot?"),
        ("assistant", "A robot is a machine..."),
        ("user", "What about humanoid robots?"),
        ("assistant", "Humanoid robots are..."),
        ("user", "Tell me about kinematics")
    ]

    # Test with max_history
    history = pipeline.build_conversation_history(messages, max_history=3)
    print(f"Conversation history ({len(history)} messages):")
    for msg in history:
        print(f"  {msg.role}: {msg.content[:50]}...")

    assert len(history) == 3
    assert history[0].content == "What about humanoid robots?"

    print("[PASS] Conversation history test passed")


def test_rag_pipeline_token_optimization():
    """Test token budget optimization."""
    print("\n=== Testing Token Budget Optimization ===")

    pipeline = RAGPipeline()

    # Create many chunks
    chunks = []
    for i in range(20):
        chunks.append(
            RetrievedChunk(
                chunk_id=uuid.uuid4(),
                content=f"This is chunk {i} with some content. " * 50,  # ~50 words
                score=1.0 - (i * 0.01),
                chapter=f"Chapter {i}",
                section=f"Section {i}",
                page=i,
                url=f"/ch{i}"
            )
        )

    # Test optimization
    optimized = pipeline.optimize_context_for_token_budget(chunks, max_tokens=1000)
    print(f"Original chunks: {len(chunks)}")
    print(f"Optimized chunks: {len(optimized)}")

    assert len(optimized) < len(chunks)
    assert len(optimized) > 0

    print("[PASS] Token budget optimization test passed")


def test_rag_pipeline_message_preparation():
    """Test complete message preparation."""
    print("\n=== Testing Message Preparation ===")

    pipeline = RAGPipeline()

    # Mock chunks
    chunks = [
        RetrievedChunk(
            chunk_id=uuid.uuid4(),
            content="Forward kinematics explanation...",
            score=0.9,
            chapter="Robot Kinematics",
            section="2.1 Forward Kinematics",
            page=42,
            url="/chapters/02-kinematics"
        )
    ]

    # Conversation history
    history = [
        ("user", "What is a robot?"),
        ("assistant", "A robot is a machine...")
    ]

    # Prepare messages
    messages = pipeline.prepare_llm_messages(
        query="What is forward kinematics?",
        chunks=chunks,
        conversation_history=history,
        selected_text=None
    )

    print(f"Prepared {len(messages)} messages:")
    for i, msg in enumerate(messages):
        print(f"  {i+1}. {msg['role']}: {len(msg['content'])} chars")

    assert len(messages) >= 3  # system + history + user
    assert messages[0]["role"] == "system"
    assert messages[-1]["role"] == "user"

    print("[PASS] Message preparation test passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("RAG PIPELINE TEST SUITE")
    print("="*60)

    tests = [
        test_retrieved_chunk,
        test_bm25,
        test_citation_extractor,
        test_sse_formatter,
        test_conversation_message,
        test_rag_pipeline_context_formatting,
        test_rag_pipeline_system_prompt,
        test_rag_pipeline_user_prompt,
        test_rag_pipeline_conversation_history,
        test_rag_pipeline_token_optimization,
        test_rag_pipeline_message_preparation
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__} failed: {e}")
            failed += 1
            import traceback
            traceback.print_exc()

    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
