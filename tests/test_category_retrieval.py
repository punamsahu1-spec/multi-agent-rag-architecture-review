from agents.category_retrieval_agent import (
    retrieve_by_category,
    format_category_retrieval_summary,
)
from agents.category_retrieval_agent import calculate_retrieval_coverage
from agents.category_retrieval_agent import (
    retrieve_by_category,
    format_category_retrieval_summary,
    calculate_retrieval_coverage,
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


def test_category_retrieval_returns_expected_source_files():
    result = retrieve_by_category(top_k_per_category=2, use_hyde=False)

    expected_source_by_category = {
        "RFC Template": "rfc_template_standard.md",
        "Security": "security_checklist.md",
        "Scalability": "scalability_reliability_standard.md",
        "Reliability": "scalability_reliability_standard.md",
        "Observability": "observability_standard.md",
        "Cost and Operations": "cost_operational_readiness.md",
    }

    for category, expected_source in expected_source_by_category.items():
        sources = [
            source["source"]
            for source in result["category_results"][category]["sources"]
        ]

        assert any(expected_source in source for source in sources), (
            f"{category} did not retrieve expected source: {expected_source}. "
            f"Actual sources: {sources}"
        )


def test_category_retrieval_reports_missing_categories_field():
    result = retrieve_by_category(top_k_per_category=2, use_hyde=False)

    assert "missing_categories" in result
    assert isinstance(result["missing_categories"], list)
def test_category_retrieval_coverage_score():
    result = retrieve_by_category(top_k_per_category=2, use_hyde=False)

    coverage = calculate_retrieval_coverage(result)

    assert coverage["total_categories"] > 0
    assert coverage["covered_categories"] > 0
    assert coverage["coverage_percent"] > 0
    assert "missing_categories" in coverage