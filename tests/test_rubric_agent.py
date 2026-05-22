from agents.rubric_agent import evaluate_rfc_with_rubric


def test_rubric_flags_weak_rfc():
    rfc_text = """
    # RFC: Customer Notification Service

    The service will use HTTPS.
    It will use Kafka and PostgreSQL.
    Application logs will be added.
    If deployment fails, we will roll back.
    """

    result = evaluate_rfc_with_rubric(rfc_text)

    assert result["numeric_score"] < 8
    assert result["decision"] in ["NEEDS_REVISION", "ARCHITECT_REVIEW"]
    assert result["critical_missing_count"] > 0


def test_rubric_approves_stronger_rfc():
    rfc_text = """
    # RFC: Strong Service Design

    Security includes authentication, authorization, encryption, PII handling,
    secrets management, and threat model.

    Scalability includes RPS, peak load, SLO, bottleneck analysis, and load testing.

    Reliability includes timeout, retry, circuit breaker, DLQ, idempotency,
    graceful degradation, disaster recovery, and backup.

    Observability includes metrics, logs, tracing, alerts, dashboard,
    runbook, and correlation ID.

    Rollback includes rollback, rollback owner, rollback time,
    and data migration rollback.

    Cost and Operations include cost, infrastructure cost, third-party cost,
    support ownership, and on-call model.
    """

    result = evaluate_rfc_with_rubric(rfc_text)

    assert result["numeric_score"] >= 8
    assert result["decision"] == "APPROVE"