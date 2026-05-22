from langchain_core.documents import Document

from agents.specialist_agents import (
    run_specialist,
    merge_specialist_reviews,
)


def make_context_docs():
    return [
        Document(
            page_content=(
                "RFC must include authentication, authorization, PII handling, "
                "encryption, secrets management, metrics, alerts, runbooks, "
                "RPS, SLOs, retry strategy, timeout strategy, and DLQ."
            ),
            metadata={
                "source": "test_standard.md",
                "chunk_id": 1,
            },
        )
    ]


def test_unknown_specialist_returns_error():
    result = run_specialist(
        specialist_type="unknown",
        rfc_text="Some RFC text",
        context_docs=make_context_docs(),
    )

    assert result["status"] == "ERROR"
    assert "Unknown specialist" in result["review"]


def test_no_context_returns_no_context():
    result = run_specialist(
        specialist_type="security",
        rfc_text="Some RFC text",
        context_docs=[],
    )

    assert result["status"] == "NO_CONTEXT"
    assert "human architect review" in result["review"].lower()


def test_merge_specialist_reviews():
    specialist_results = {
        "security": {
            "status": "OK",
            "review": "Security review content",
        },
        "observability": {
            "status": "OK",
            "review": "Observability review content",
        },
    }

    merged = merge_specialist_reviews(specialist_results)

    assert "Specialist Agent Reviews" in merged
    assert "Security review content" in merged
    assert "Observability review content" in merged