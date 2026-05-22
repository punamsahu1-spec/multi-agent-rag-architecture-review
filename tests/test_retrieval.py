from agents.ingest_agent import seed_standards
from agents.retrieval_agent import retrieve_with_fallback, format_retrieved_docs


def test_retrieve_security_requirements():
    seed_standards()

    docs, status = retrieve_with_fallback(
        "What security requirements must an RFC include?",
        use_hyde=False,
        top_k=3,
    )

    assert status in ["OK_DIRECT_MMR", "OK_HYDE_MMR"]
    assert len(docs) > 0

    content = " ".join(doc.page_content.lower() for doc in docs)

    assert (
        "security" in content
        or "authentication" in content
        or "authorization" in content
        or "encryption" in content
    )


def test_retrieve_observability_requirements():
    seed_standards()

    docs, status = retrieve_with_fallback(
        "What observability requirements should be included in an RFC?",
        use_hyde=False,
        top_k=3,
    )

    assert status in ["OK_DIRECT_MMR", "OK_HYDE_MMR"]
    assert len(docs) > 0

    content = " ".join(doc.page_content.lower() for doc in docs)

    assert (
        "observability" in content
        or "metrics" in content
        or "tracing" in content
        or "alerts" in content
        or "runbook" in content
    )


def test_format_retrieved_docs():
    seed_standards()

    docs, _ = retrieve_with_fallback(
        "rollback strategy owner timeline",
        use_hyde=False,
        top_k=2,
    )

    formatted = format_retrieved_docs(docs)

    assert "Source" in formatted
    assert "chunk_id" in formatted
    assert len(formatted) > 50