from typing import List
from langchain_core.documents import Document


def _format_evidence(retrieved_docs: List[Document], max_docs: int = 5) -> str:
    if not retrieved_docs:
        return "- No retrieved standards available."

    evidence_lines = []

    seen = set()

    for doc in retrieved_docs:
        source = doc.metadata.get("source", "unknown")
        chunk_id = doc.metadata.get("chunk_id", "unknown")
        key = f"{source}:{chunk_id}"

        if key in seen:
            continue

        seen.add(key)

        snippet = doc.page_content.strip().replace("\n", " ")
        snippet = snippet[:300] + "..." if len(snippet) > 300 else snippet

        evidence_lines.append(
            f"- **{source} / chunk {chunk_id}:** {snippet}"
        )

        if len(evidence_lines) >= max_docs:
            break

    return "\n".join(evidence_lines)


def _format_dimension_gaps(rubric_result: dict) -> str:
    dimension_checks = rubric_result.get("dimension_checks", [])

    if not dimension_checks:
        return "- No rubric dimension details available."

    lines = []

    for check in dimension_checks:
        dimension = check.get("dimension", "Unknown")
        status = check.get("status", "UNKNOWN")
        missing = check.get("missing_signals", [])

        if status == "PASS":
            lines.append(f"- **{dimension}: PASS** — Key signals are present.")
        else:
            missing_text = ", ".join(missing[:8]) if missing else "Not specified"
            lines.append(
                f"- **{dimension}: {status}** — Missing signals: {missing_text}."
            )

    return "\n".join(lines)


def generate_demo_review(
    rfc_text: str,
    rubric_result: dict,
    retrieved_docs: List[Document],
) -> str:
    """
    Generates a local demo-safe RFC review report.
    No external LLM call is made.
    """

    score = rubric_result.get("rubric_score", "N/A")
    decision = rubric_result.get("decision", "ARCHITECT_REVIEW")
    human_review = rubric_result.get("human_review_required", "YES")
    critical_missing = rubric_result.get("critical_missing_count", 0)
    major_gaps = rubric_result.get("major_gap_count", 0)

    evidence = _format_evidence(retrieved_docs)
    dimension_gaps = _format_dimension_gaps(rubric_result)

    if decision == "APPROVE":
        summary = (
            "The RFC appears broadly ready based on the deterministic rubric. "
            "Minor review may still be useful before final approval."
        )
    elif decision == "NEEDS_REVISION":
        summary = (
            "The RFC has important architecture gaps and should be revised before "
            "formal architect review."
        )
    else:
        summary = (
            "The RFC has significant missing architecture signals and should be "
            "escalated for human architect review."
        )

    return f"""
# RFC Review Report

## Execution Mode
DEMO_MODE — Local rule-based review. No external LLM call was made.

## Overall Score
{score}

## Approval Status
{decision}

## Executive Summary
- {summary}
- Critical missing signal count: {critical_missing}
- Major gap count: {major_gaps}
- The decision is calculated using the deterministic rubric, not an LLM-only judgment.

## Section / Dimension Completeness

{dimension_gaps}

## Evidence From Retrieved Standards

{evidence}

## Recommended Next Steps
- Strengthen all dimensions marked PARTIAL or MISSING.
- Add measurable security, scalability, reliability, observability, rollback, and cost details.
- Re-run the review after revising the RFC.
- Use human architect review for high-risk or production-impacting systems.

## Human Review Required?
{human_review}

## Reason
Human review is required when the rubric score is low, critical signals are missing, or the RFC lacks sufficient architecture-readiness evidence.
""".strip()