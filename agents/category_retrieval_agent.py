from typing import Dict, List, Tuple

from langchain_core.documents import Document

from agents.retrieval_agent import retrieve_with_fallback, format_retrieved_docs


REVIEW_CATEGORY_QUERIES = {
    "RFC Template": (
        "RFC template required sections problem statement proposed solution "
        "alternatives tradeoffs dependencies rollback risks approval owners"
    ),
    "Security": (
        "security requirements authentication authorization encryption PII "
        "secrets management threat model audit logging"
    ),
    "Scalability": (
        "scalability requirements RPS peak load users data volume scaling strategy "
        "bottlenecks load testing"
    ),
    "Reliability": (
        "reliability requirements timeout retry circuit breaker DLQ idempotency "
        "graceful degradation disaster recovery backup"
    ),
    "Observability": (
        "observability requirements metrics logs tracing correlation ID alerts "
        "dashboards runbooks escalation path noisy alerts"
    ),
    "Rollback": (
        "rollback requirements rollback procedure rollback owner rollback time "
        "data migration rollback deployment rollback"
    ),
    "Cost and Operations": (
        "cost operational readiness infrastructure cost third party cost support ownership "
        "on-call release communication deployment approach governance"
    ),
}


def _doc_key(doc: Document) -> str:
    """
    Creates a stable deduplication key for retrieved chunks.
    """
    source = doc.metadata.get("source", "unknown")
    chunk_id = doc.metadata.get("chunk_id", "unknown")
    return f"{source}:{chunk_id}"


def dedupe_docs(docs: List[Document]) -> List[Document]:
    """
    Removes duplicate retrieved chunks using source + chunk_id.
    """
    seen = set()
    unique_docs = []

    for doc in docs:
        key = _doc_key(doc)

        if key in seen:
            continue

        seen.add(key)
        unique_docs.append(doc)

    return unique_docs


def retrieve_by_category(
    top_k_per_category: int = 3,
    use_hyde: bool = False,
) -> Dict:
    """
    Retrieves standards context separately for each architecture review category.

    Why:
    A single broad query can over-retrieve one document type.
    Category-wise retrieval ensures balanced context across RFC template,
    security, scalability, reliability, observability, rollback, and operations.
    """

    category_results = {}
    all_docs = []
    missing_categories = []

    for category, query in REVIEW_CATEGORY_QUERIES.items():
        docs, status = retrieve_with_fallback(
            query=query,
            use_hyde=use_hyde,
            top_k=top_k_per_category,
        )

        unique_category_docs = dedupe_docs(docs)

        category_results[category] = {
            "query": query,
            "status": status,
            "docs_count": len(unique_category_docs),
            "sources": [
                {
                    "source": doc.metadata.get("source", "unknown"),
                    "chunk_id": doc.metadata.get("chunk_id", "unknown"),
                }
                for doc in unique_category_docs
            ],
            "docs": unique_category_docs,
        }

        if not unique_category_docs:
            missing_categories.append(category)

        all_docs.extend(unique_category_docs)

    all_unique_docs = dedupe_docs(all_docs)

    return {
        "all_unique_docs": all_unique_docs,
        "category_results": category_results,
        "missing_categories": missing_categories,
        "total_unique_chunks": len(all_unique_docs),
    }


def format_category_retrieval_summary(category_retrieval_result: Dict) -> str:
    """
    Creates a markdown summary of category-wise retrieval.
    """

    lines = ["# Category-wise Retrieval Summary"]

    lines.append(
        f"\nTotal unique chunks retrieved: "
        f"{category_retrieval_result.get('total_unique_chunks', 0)}"
    )

    missing = category_retrieval_result.get("missing_categories", [])

    if missing:
        lines.append("\n## Missing Categories")
        for category in missing:
            lines.append(f"- {category}")
    else:
        lines.append("\nNo missing categories. All review categories returned context.")

    lines.append("\n## Category Results")

    category_results = category_retrieval_result.get("category_results", {})

    for category, result in category_results.items():
        lines.append(f"\n### {category}")
        lines.append(f"- Status: {result.get('status')}")
        lines.append(f"- Unique chunks: {result.get('docs_count')}")

        sources = result.get("sources", [])

        if sources:
            lines.append("- Sources:")
            for source in sources:
                lines.append(
                    f"  - {source.get('source')} / chunk {source.get('chunk_id')}"
                )
        else:
            lines.append("- Sources: None")

    return "\n".join(lines)


def format_category_retrieved_docs(category_retrieval_result: Dict) -> str:
    """
    Formats all unique category-retrieved docs for prompt context.
    """
    docs = category_retrieval_result.get("all_unique_docs", [])
    return format_retrieved_docs(docs)


if __name__ == "__main__":
    result = retrieve_by_category(top_k_per_category=2, use_hyde=False)

    print(format_category_retrieval_summary(result))

    print("\n--- FORMATTED CONTEXT ---\n")
    print(format_category_retrieved_docs(result))