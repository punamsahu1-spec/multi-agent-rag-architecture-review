import re
from typing import Dict, List


def contains_any(text: str, keywords: List[str]) -> bool:
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)


def check_dimension(
    rfc_text: str,
    dimension: str,
    required_signals: List[str],
    critical_signals: List[str] = None,
) -> Dict:
    """
    Checks whether an RFC contains enough signals for a review dimension.
    """
    critical_signals = critical_signals or []

    found = [
        signal for signal in required_signals
        if signal.lower() in rfc_text.lower()
    ]

    missing = [
        signal for signal in required_signals
        if signal.lower() not in rfc_text.lower()
    ]

    critical_missing = [
        signal for signal in critical_signals
        if signal.lower() not in rfc_text.lower()
    ]

    if len(missing) == 0:
        status = "PASS"
    elif len(found) > 0:
        status = "PARTIAL"
    else:
        status = "MISSING"

    return {
        "dimension": dimension,
        "status": status,
        "found_signals": found,
        "missing_signals": missing,
        "critical_missing": critical_missing,
    }


def evaluate_rfc_with_rubric(rfc_text: str) -> Dict:
    """
    Deterministic RFC readiness scoring.

    Score starts at 10.
    Deductions are based on missing architecture signals.
    """

    checks = []

    checks.append(
        check_dimension(
            rfc_text,
            "Security",
            required_signals=[
                "authentication",
                "authorization",
                "encryption",
                "PII",
                "secrets",
                "threat model",
            ],
            critical_signals=[
                "authentication",
                "authorization",
                "PII",
                "secrets",
            ],
        )
    )

    checks.append(
        check_dimension(
            rfc_text,
            "Scalability",
            required_signals=[
                "RPS",
                "peak load",
                "SLO",
                "bottleneck",
                "load testing",
            ],
            critical_signals=[
                "RPS",
                "peak load",
                "SLO",
            ],
        )
    )

    checks.append(
        check_dimension(
            rfc_text,
            "Reliability",
            required_signals=[
                "timeout",
                "retry",
                "circuit breaker",
                "dead-letter",
                "DLQ",
                "idempotency",
                "graceful degradation",
                "disaster recovery",
                "backup",
            ],
            critical_signals=[
                "timeout",
                "retry",
                "DLQ",
                "idempotency",
            ],
        )
    )

    checks.append(
        check_dimension(
            rfc_text,
            "Observability",
            required_signals=[
                "metrics",
                "logs",
                "tracing",
                "alerts",
                "dashboard",
                "runbook",
                "correlation ID",
            ],
            critical_signals=[
                "metrics",
                "alerts",
                "runbook",
            ],
        )
    )

    checks.append(
        check_dimension(
            rfc_text,
            "Rollback",
            required_signals=[
                "rollback",
                "rollback owner",
                "rollback time",
                "data migration rollback",
            ],
            critical_signals=[
                "rollback",
                "rollback owner",
            ],
        )
    )

    checks.append(
        check_dimension(
            rfc_text,
            "Cost and Operations",
            required_signals=[
                "cost",
                "infrastructure cost",
                "third-party cost",
                "support ownership",
                "on-call",
            ],
            critical_signals=[
                "cost",
                "support ownership",
            ],
        )
    )

    score = 10
    critical_missing_count = 0
    major_gap_count = 0

    for check in checks:
        if check["status"] == "MISSING":
            score -= 2
            major_gap_count += 1
        elif check["status"] == "PARTIAL":
            score -= 1

        critical_missing_count += len(check["critical_missing"])

    score = max(score, 1)

    if critical_missing_count >= 6 or score <= 4:
        decision = "ARCHITECT_REVIEW"
        human_review_required = "YES"
    elif major_gap_count > 0 or score < 8:
        decision = "NEEDS_REVISION"
        human_review_required = "NO"
    else:
        decision = "APPROVE"
        human_review_required = "NO"

    return {
        "rubric_score": f"{score}/10",
        "numeric_score": score,
        "decision": decision,
        "human_review_required": human_review_required,
        "critical_missing_count": critical_missing_count,
        "major_gap_count": major_gap_count,
        "dimension_checks": checks,
    }


if __name__ == "__main__":
    sample = """
    The service will use HTTPS.
    It will use Kafka and PostgreSQL.
    Application logs will be added.
    If deployment fails, we will roll back.
    """

    result = evaluate_rfc_with_rubric(sample)
    print(result)