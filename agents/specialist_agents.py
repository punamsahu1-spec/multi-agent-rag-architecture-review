from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SpecialistFinding:
    agent: str
    status: str
    score: int
    findings: list[str]
    recommendations: list[str]


def _contains_any(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)


def _score_from_findings(total_checks: int, passed_checks: int) -> int:
    if total_checks == 0:
        return 0
    return round((passed_checks / total_checks) * 10)


def security_specialist(rfc_text: str) -> SpecialistFinding:
    checks = {
        "Authentication and authorization are described": [
            "authentication",
            "authorization",
            "auth",
            "oauth",
            "jwt",
            "sso",
            "rbac",
        ],
        "Secrets and credentials are handled safely": [
            "secret",
            "credential",
            "key vault",
            "vault",
            "kms",
            "managed identity",
        ],
        "Sensitive data or PII protection is addressed": [
            "pii",
            "personal data",
            "encryption",
            "masking",
            "tokenization",
            "data privacy",
        ],
        "Network or API protection is considered": [
            "rate limit",
            "waf",
            "api gateway",
            "tls",
            "https",
            "firewall",
        ],
    }

    findings = []
    recommendations = []
    passed = 0

    for check, keywords in checks.items():
        if _contains_any(rfc_text, keywords):
            findings.append(f"✅ {check}")
            passed += 1
        else:
            findings.append(f"⚠️ Missing: {check}")
            recommendations.append(f"Add details for: {check}")

    score = _score_from_findings(len(checks), passed)
    status = "PASS" if score >= 7 else "NEEDS_REVIEW"

    return SpecialistFinding(
        agent="Security Specialist",
        status=status,
        score=score,
        findings=findings,
        recommendations=recommendations,
    )


def scalability_specialist(rfc_text: str) -> SpecialistFinding:
    checks = {
        "Expected load or traffic is described": [
            "rps",
            "qps",
            "tps",
            "throughput",
            "traffic",
            "load",
            "concurrency",
        ],
        "Scaling strategy is described": [
            "autoscale",
            "auto scale",
            "horizontal scaling",
            "scale out",
            "partition",
            "shard",
        ],
        "Performance constraints are considered": [
            "latency",
            "p95",
            "p99",
            "response time",
            "sla",
            "slo",
        ],
        "Capacity or bottleneck risks are considered": [
            "capacity",
            "bottleneck",
            "queue",
            "backpressure",
            "throttle",
        ],
    }

    findings = []
    recommendations = []
    passed = 0

    for check, keywords in checks.items():
        if _contains_any(rfc_text, keywords):
            findings.append(f"✅ {check}")
            passed += 1
        else:
            findings.append(f"⚠️ Missing: {check}")
            recommendations.append(f"Add details for: {check}")

    score = _score_from_findings(len(checks), passed)
    status = "PASS" if score >= 7 else "NEEDS_REVIEW"

    return SpecialistFinding(
        agent="Scalability Specialist",
        status=status,
        score=score,
        findings=findings,
        recommendations=recommendations,
    )


def reliability_specialist(rfc_text: str) -> SpecialistFinding:
    checks = {
        "Failure modes are described": [
            "failure",
            "failure mode",
            "outage",
            "degraded",
            "fallback",
        ],
        "Retry and timeout strategy is considered": [
            "retry",
            "timeout",
            "circuit breaker",
            "exponential backoff",
        ],
        "High availability or resilience is addressed": [
            "high availability",
            "ha",
            "resilience",
            "redundancy",
            "multi-zone",
            "multi region",
        ],
        "Recovery and disaster recovery are considered": [
            "recovery",
            "rto",
            "rpo",
            "disaster recovery",
            "backup",
            "restore",
        ],
    }

    findings = []
    recommendations = []
    passed = 0

    for check, keywords in checks.items():
        if _contains_any(rfc_text, keywords):
            findings.append(f"✅ {check}")
            passed += 1
        else:
            findings.append(f"⚠️ Missing: {check}")
            recommendations.append(f"Add details for: {check}")

    score = _score_from_findings(len(checks), passed)
    status = "PASS" if score >= 7 else "NEEDS_REVIEW"

    return SpecialistFinding(
        agent="Reliability Specialist",
        status=status,
        score=score,
        findings=findings,
        recommendations=recommendations,
    )


def observability_specialist(rfc_text: str) -> SpecialistFinding:
    checks = {
        "Logging strategy is described": [
            "log",
            "logging",
            "structured log",
            "correlation id",
        ],
        "Metrics are described": [
            "metric",
            "metrics",
            "dashboard",
            "kpi",
            "sli",
        ],
        "Tracing is described": [
            "trace",
            "tracing",
            "distributed tracing",
            "opentelemetry",
        ],
        "Alerting or runbook is described": [
            "alert",
            "alerting",
            "runbook",
            "on-call",
            "incident",
        ],
    }

    findings = []
    recommendations = []
    passed = 0

    for check, keywords in checks.items():
        if _contains_any(rfc_text, keywords):
            findings.append(f"✅ {check}")
            passed += 1
        else:
            findings.append(f"⚠️ Missing: {check}")
            recommendations.append(f"Add details for: {check}")

    score = _score_from_findings(len(checks), passed)
    status = "PASS" if score >= 7 else "NEEDS_REVIEW"

    return SpecialistFinding(
        agent="Observability Specialist",
        status=status,
        score=score,
        findings=findings,
        recommendations=recommendations,
    )


def cost_operations_specialist(rfc_text: str) -> SpecialistFinding:
    checks = {
        "Cost impact is considered": [
            "cost",
            "budget",
            "finops",
            "pricing",
            "compute cost",
            "storage cost",
        ],
        "Operational ownership is defined": [
            "owner",
            "ownership",
            "support team",
            "on-call",
            "operational owner",
        ],
        "Deployment and support model is described": [
            "deployment",
            "release",
            "support",
            "maintenance",
            "operations",
        ],
        "Capacity or usage monitoring is planned": [
            "capacity",
            "usage",
            "monitoring",
            "quota",
            "limit",
        ],
    }

    findings = []
    recommendations = []
    passed = 0

    for check, keywords in checks.items():
        if _contains_any(rfc_text, keywords):
            findings.append(f"✅ {check}")
            passed += 1
        else:
            findings.append(f"⚠️ Missing: {check}")
            recommendations.append(f"Add details for: {check}")

    score = _score_from_findings(len(checks), passed)
    status = "PASS" if score >= 7 else "NEEDS_REVIEW"

    return SpecialistFinding(
        agent="Cost & Operations Specialist",
        status=status,
        score=score,
        findings=findings,
        recommendations=recommendations,
    )


def rollback_specialist(rfc_text: str) -> SpecialistFinding:
    checks = {
        "Rollback strategy is described": [
            "rollback",
            "roll back",
            "revert",
            "backout",
        ],
        "Deployment safety is considered": [
            "blue green",
            "blue-green",
            "canary",
            "feature flag",
            "progressive rollout",
        ],
        "Data migration rollback is considered": [
            "migration",
            "schema change",
            "backward compatible",
            "data rollback",
        ],
        "Validation after release is described": [
            "validation",
            "smoke test",
            "post deployment",
            "health check",
            "verification",
        ],
    }

    findings = []
    recommendations = []
    passed = 0

    for check, keywords in checks.items():
        if _contains_any(rfc_text, keywords):
            findings.append(f"✅ {check}")
            passed += 1
        else:
            findings.append(f"⚠️ Missing: {check}")
            recommendations.append(f"Add details for: {check}")

    score = _score_from_findings(len(checks), passed)
    status = "PASS" if score >= 7 else "NEEDS_REVIEW"

    return SpecialistFinding(
        agent="Rollback Specialist",
        status=status,
        score=score,
        findings=findings,
        recommendations=recommendations,
    )


def run_specialist_review(rfc_text: str) -> dict[str, Any]:
    """
    Runs all specialist agents and returns a structured multi-agent review.

    This is intentionally deterministic and lightweight so the demo is explainable.
    The LLM can write the review, but these agents provide consistent review signals.
    """

    specialists = [
        security_specialist(rfc_text),
        scalability_specialist(rfc_text),
        reliability_specialist(rfc_text),
        observability_specialist(rfc_text),
        cost_operations_specialist(rfc_text),
        rollback_specialist(rfc_text),
    ]

    average_score = round(
        sum(agent.score for agent in specialists) / len(specialists),
        2,
    )

    needs_review = [
        agent.agent
        for agent in specialists
        if agent.status != "PASS"
    ]

    if average_score >= 8 and not needs_review:
        overall_status = "PASS"
    elif average_score >= 6:
        overall_status = "ARCHITECT_REVIEW"
    else:
        overall_status = "REWORK_REQUIRED"

    return {
        "overall_status": overall_status,
        "average_score": average_score,
        "needs_review": needs_review,
        "specialist_findings": [
            {
                "agent": agent.agent,
                "status": agent.status,
                "score": agent.score,
                "findings": agent.findings,
                "recommendations": agent.recommendations,
            }
            for agent in specialists
        ],
    }


if __name__ == "__main__":
    sample_rfc = """
    This RFC proposes a new customer notification service.
    The service uses OAuth authentication, structured logging,
    autoscale, p95 latency SLO, retries, timeout, alerts,
    rollback using feature flags, and operational ownership.
    """

    review = run_specialist_review(sample_rfc)

    from pprint import pprint

    pprint(review)