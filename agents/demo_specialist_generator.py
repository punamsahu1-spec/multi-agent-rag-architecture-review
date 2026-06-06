from typing import Dict


def _get_dimension_check(rubric_result: dict, dimension_name: str) -> dict:
    checks = rubric_result.get("dimension_checks", [])

    for check in checks:
        if check.get("dimension", "").lower() == dimension_name.lower():
            return check

    return {
        "dimension": dimension_name,
        "status": "UNKNOWN",
        "missing_signals": [],
        "critical_missing": [],
    }


def _build_specialist_review(title: str, check: dict) -> str:
    status = check.get("status", "UNKNOWN")
    missing = check.get("missing_signals", [])
    critical_missing = check.get("critical_missing", [])

    if status == "PASS":
        summary = f"{title} appears broadly covered based on the deterministic rubric."
    elif status == "PARTIAL":
        summary = f"{title} is partially covered but needs more detail before approval."
    else:
        summary = f"{title} is missing or insufficiently described in the RFC."

    missing_text = ", ".join(missing) if missing else "No major missing signals identified."
    critical_text = (
        ", ".join(critical_missing)
        if critical_missing
        else "No critical missing signals identified."
    )

    return f"""
## {title} Review

### Status
{status}

### Key Findings
- {summary}

### Critical Gaps
- {critical_text}

### Missing Signals
- {missing_text}

### Recommendations
- Add clear details for all missing signals.
- Ensure the RFC explains ownership, design choices, risks, and operational impact.
- Re-run the review after updating the RFC.

### Evidence Basis
- Demo-safe review generated from deterministic rubric signals.
""".strip()


def run_demo_specialists(rubric_result: dict) -> Dict[str, Dict[str, str]]:
    """
    Demo-safe specialist reviews.
    No external LLM call.
    """

    security_check = _get_dimension_check(rubric_result, "Security")
    scalability_check = _get_dimension_check(rubric_result, "Scalability")
    reliability_check = _get_dimension_check(rubric_result, "Reliability")
    observability_check = _get_dimension_check(rubric_result, "Observability")

    scalability_reliability_review = (
        _build_specialist_review("Scalability", scalability_check)
        + "\n\n"
        + _build_specialist_review("Reliability", reliability_check)
    )

    return {
        "security": {
            "specialist": "security",
            "status": "OK",
            "review": _build_specialist_review("Security", security_check),
        },
        "scalability": {
            "specialist": "scalability",
            "status": "OK",
            "review": scalability_reliability_review,
        },
        "observability": {
            "specialist": "observability",
            "status": "OK",
            "review": _build_specialist_review("Observability", observability_check),
        },
    }


def merge_demo_specialist_reviews(specialist_results: Dict[str, Dict[str, str]]) -> str:
    sections = ["# Specialist Agent Reviews"]

    for specialist, result in specialist_results.items():
        sections.append(f"\n---\n\n## {specialist.title()} Agent")
        sections.append(f"Status: {result.get('status', 'UNKNOWN')}")
        sections.append(result.get("review", ""))

    return "\n\n".join(sections)