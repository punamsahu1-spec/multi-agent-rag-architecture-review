from agents.supervisor_agent import (
    decide_final_recommendation,
    format_supervisor_summary,
)


def test_supervisor_routes_low_score_to_architect_review():
    rubric_result = {
        "numeric_score": 3,
        "rubric_score": "3/10",
        "decision": "ARCHITECT_REVIEW",
        "critical_missing_count": 8,
        "major_gap_count": 2,
    }

    specialist_results = {
        "security": {"status": "OK"},
        "scalability": {"status": "OK"},
        "observability": {"status": "OK"},
    }

    result = decide_final_recommendation(rubric_result, specialist_results)

    assert result["final_decision"] == "ARCHITECT_REVIEW"
    assert result["human_review_required"] == "YES"


def test_supervisor_routes_medium_score_to_needs_revision():
    rubric_result = {
        "numeric_score": 7,
        "rubric_score": "7/10",
        "decision": "NEEDS_REVISION",
        "critical_missing_count": 2,
        "major_gap_count": 1,
    }

    specialist_results = {
        "security": {"status": "OK"},
        "scalability": {"status": "OK"},
        "observability": {"status": "OK"},
    }

    result = decide_final_recommendation(rubric_result, specialist_results)

    assert result["final_decision"] == "NEEDS_REVISION"
    assert result["human_review_required"] == "NO"


def test_supervisor_approves_strong_rfc():
    rubric_result = {
        "numeric_score": 9,
        "rubric_score": "9/10",
        "decision": "APPROVE",
        "critical_missing_count": 0,
        "major_gap_count": 0,
    }

    specialist_results = {
        "security": {"status": "OK"},
        "scalability": {"status": "OK"},
        "observability": {"status": "OK"},
    }

    result = decide_final_recommendation(rubric_result, specialist_results)

    assert result["final_decision"] == "APPROVE"
    assert result["human_review_required"] == "NO"


def test_supervisor_escalates_specialist_failure():
    rubric_result = {
        "numeric_score": 9,
        "rubric_score": "9/10",
        "decision": "APPROVE",
        "critical_missing_count": 0,
        "major_gap_count": 0,
    }

    specialist_results = {
        "security": {"status": "OK"},
        "scalability": {"status": "NO_CONTEXT"},
        "observability": {"status": "OK"},
    }

    result = decide_final_recommendation(rubric_result, specialist_results)

    assert result["final_decision"] == "ARCHITECT_REVIEW"
    assert result["human_review_required"] == "YES"


def test_format_supervisor_summary():
    supervisor_result = {
        "final_decision": "ARCHITECT_REVIEW",
        "human_review_required": "YES",
        "reason": "Critical gaps found.",
        "rubric_score": "3/10",
        "rubric_decision": "ARCHITECT_REVIEW",
        "critical_missing_count": 8,
        "major_gap_count": 2,
    }

    summary = format_supervisor_summary(supervisor_result)

    assert "Supervisor Final Recommendation" in summary
    assert "ARCHITECT_REVIEW" in summary
    assert "3/10" in summary