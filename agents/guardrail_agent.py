import re


INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore above",
    "disregard your system prompt",
    "reveal your system prompt",
    "you are now",
    "act as dan",
    "forget everything",
    "new persona",
    "pretend you are",
    "jailbreak",
    "bypass",
    "override instructions",
    "developer mode",
    "sudo mode",
]


def input_guard(text: str) -> dict:
    """
    Checks whether the input is safe before sending it to the LLM.
    """

    if not text or not text.strip():
        return {
            "safe": False,
            "reason": "Empty input."
        }

    if len(text) > 100_000:
        return {
            "safe": False,
            "reason": f"Input too large: {len(text)} characters. Max allowed is 100000."
        }

    text_lower = text.lower()

    for pattern in INJECTION_PATTERNS:
        if pattern in text_lower:
            return {
                "safe": False,
                "reason": f"Prompt injection detected: {pattern}"
            }

    return {
        "safe": True,
        "reason": "Input passed guardrail checks."
    }


def output_guard(response: str) -> str:
    """
    Redacts common sensitive patterns from the LLM output.
    This is a lightweight MVP guardrail.
    """

    if not response:
        return response

    # Redact email addresses.
    response = re.sub(
        r"\b[\w\.-]+@[\w\.-]+\.\w+\b",
        "[REDACTED_EMAIL]",
        response,
    )

    # Redact phone-like numbers.
    response = re.sub(
        r"\b(?:\+?\d[\d\s\-().]{8,}\d)\b",
        "[REDACTED_PHONE]",
        response,
    )

    # Redact common API key style tokens.
    response = re.sub(
        r"\bAIza[0-9A-Za-z_\-]{20,}\b",
        "[REDACTED_GOOGLE_API_KEY]",
        response,
    )

    response = re.sub(
        r"\bls[v2]?_pt_[0-9A-Za-z_\-]{20,}\b",
        "[REDACTED_LANGSMITH_KEY]",
        response,
    )

    return response


def sanitize_filename(filename: str) -> str:
    """
    Prevents unsafe file names and path traversal.
    """

    return re.sub(r"[^\w\-. ]", "_", filename)