from typing import Dict


def decide_final_recommendation(
    rubric_result: Dict,
    specialist_results: Dict[str, Dict[str, str]],
) -> Dict:
    """
    Deterministic supervisor decision.

    The supervisor uses the rubric score and specialist statuses
    to decide the final architecture recommendation.
    """

    numeric_score = rubric_result.get("numeric_score", 0)
    rubric_decision = rubric_result.get("decision", "ARCHITECT_REVIEW")
    critical_missing_count = rubric_result.get("critical_missing_count", 0)
    major_gap_count = rubric_result.get("major_gap_count", 0)

    specialist_statuses = [
        result.get("status", "UNKNOWN")
        for result in specialist_results.values()
    ]

    if "NO_CONTEXT" in specialist_statuses or "ERROR" in specialist_statuses:
        final_decision = "ARCHITECT_REVIEW"
        human_review_required = "YES"
        reason = (
            "One or more specialist agents could not complete review due to missing "
            "context or execution error."
        )

    elif rubric_decision == "ARCHITECT_REVIEW":
        final_decision = "ARCHITECT_REVIEW"
        human_review_required = "YES"
        reason = (
            "The deterministic rubric identified critical missing architecture signals "
            "or a low readiness score."
        )

    elif numeric_score < 8 or major_gap_count > 0:
        final_decision = "NEEDS_REVISION"
        human_review_required = "NO"
        reason = (
            "The RFC has important gaps and should be revised before senior architect review."
        )

    else:
        final_decision = "APPROVE"
        human_review_required = "NO"
        reason = (
            "The RFC meets the minimum architecture readiness criteria in the MVP rubric."
        )

    return {
        "final_decision": final_decision,
        "human_review_required": human_review_required,
        "reason": reason,
        "rubric_score": rubric_result.get("rubric_score"),
        "rubric_decision": rubric_decision,
        "critical_missing_count": critical_missing_count,
        "major_gap_count": major_gap_count,
        "specialist_statuses": {
            specialist: result.get("status", "UNKNOWN")
            for specialist, result in specialist_results.items()
        },
    }


def format_supervisor_summary(supervisor_result: Dict) -> str:
    """
    Formats supervisor result as markdown for UI/report.
    """

    return f"""
# Supervisor Final Recommendation

## Final Decision
{supervisor_result["final_decision"]}

## Human Review Required
{supervisor_result["human_review_required"]}

## Reason
{supervisor_result["reason"]}

## Rubric Score
{supervisor_result["rubric_score"]}

## Rubric Decision
{supervisor_result["rubric_decision"]}

## Critical Missing Count
{supervisor_result["critical_missing_count"]}

## Major Gap Count
{supervisor_result["major_gap_count"]}
""".strip()