from agents.category_retrieval_agent import (
    retrieve_by_category,
    format_category_retrieval_summary,
)


def test_category_retrieval_returns_all_categories():
    result = retrieve_by_category(top_k_per_category=2, use_hyde=False)

    category_results = result["category_results"]

    expected_categories = [
        "RFC Template",
        "Security",
        "Scalability",
        "Reliability",
        "Observability",
        "Rollback",
        "Cost and Operations",
    ]

    for category in expected_categories:
        assert category in category_results
        assert category_results[category]["docs_count"] > 0


def test_category_retrieval_deduplicates_chunks():
    result = retrieve_by_category(top_k_per_category=3, use_hyde=False)

    docs = result["all_unique_docs"]

    keys = [
        f"{doc.metadata.get('source')}:{doc.metadata.get('chunk_id')}"
        for doc in docs
    ]

    assert len(keys) == len(set(keys))


def test_category_retrieval_summary_has_categories():
    result = retrieve_by_category(top_k_per_category=1, use_hyde=False)

    summary = format_category_retrieval_summary(result)

    assert "Category-wise Retrieval Summary" in summary
    assert "Security" in summary
    assert "Observability" in summary
    assert "Cost and Operations" in summary