from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "logs/review_audit.jsonl")


def write_review_audit_event(event: dict[str, Any]) -> None:
    path = Path(AUDIT_LOG_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)

    audit_event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **event,
    }

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(audit_event, ensure_ascii=False) + "\n")


def read_recent_audit_events(limit: int = 20) -> list[dict[str, Any]]:
    path = Path(AUDIT_LOG_PATH)

    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    recent_lines = lines[-limit:]

    events: list[dict[str, Any]] = []

    for line in recent_lines:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return events


def build_review_audit_event(
    rfc_id: str,
    user_id: str,
    rfc_text: str,
    retrieved_sources: list[Any] | None = None,
    specialist_results: dict[str, Any] | None = None,
    rubric_result: dict[str, Any] | None = None,
    supervisor_decision: dict[str, Any] | str | None = None,
    guardrail_result: dict[str, Any] | None = None,
    review_summary: str | None = None,
) -> dict[str, Any]:
    return {
        "rfc_id": rfc_id,
        "user_id": user_id,
        "rfc_length_chars": len(rfc_text or ""),
        "retrieved_sources": retrieved_sources or [],
        "specialist_results": specialist_results or {},
        "rubric_result": rubric_result or {},
        "supervisor_decision": supervisor_decision,
        "guardrail_result": guardrail_result or {},
        "review_summary": review_summary,
    }


if __name__ == "__main__":
    sample_event = build_review_audit_event(
        rfc_id="RFC-DEMO-001",
        user_id="demo_user",
        rfc_text="Sample RFC for audit logging demo.",
        retrieved_sources=["security_standards.md", "observability_standards.md"],
        specialist_results={
            "security": {"status": "NEEDS_REVIEW", "score": 5},
            "observability": {"status": "PASS", "score": 8},
        },
        rubric_result={"score": "6/10", "decision": "ARCHITECT_REVIEW"},
        supervisor_decision="ARCHITECT_REVIEW",
        guardrail_result={"allowed": True, "risk_level": "LOW"},
        review_summary="Demo audit event.",
    )

    write_review_audit_event(sample_event)

    print("Recent audit events:")
    for event in read_recent_audit_events(limit=3):
        print(event)