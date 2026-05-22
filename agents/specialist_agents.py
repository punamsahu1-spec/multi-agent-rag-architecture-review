import os
from typing import Dict, List

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.guardrail_agent import output_guard
from agents.retrieval_agent import format_retrieved_docs


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY is missing. Add it to .env in the project root."
    )


def make_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.1,
    )


SPECIALIST_PROMPTS = {
    "security": """
You are a CISO-level security architect.

Review ONLY the security aspects of the RFC.

Check:
- Authentication
- Authorization
- Threat model
- PII handling
- Encryption at rest and in transit
- Secrets management
- OWASP-style application risks
- Audit logging

Return this exact structure:

## Security Review

### Security Score
X/10

### Key Findings
- ...

### Critical Gaps
- ...

### Recommendations
- ...

### Evidence From Standards
- ...
""",
    "scalability": """
You are a senior distributed systems architect.

Review ONLY scalability and reliability aspects of the RFC.

Check:
- RPS / peak load
- User or data growth
- Scaling strategy
- Bottlenecks
- SLOs / SLIs
- Timeout strategy
- Retry strategy
- Circuit breaker
- DLQ / dead-letter queue
- Idempotency
- Graceful degradation
- Disaster recovery / backup

Return this exact structure:

## Scalability and Reliability Review

### Scalability/Reliability Score
X/10

### Key Findings
- ...

### Critical Gaps
- ...

### Recommendations
- ...

### Evidence From Standards
- ...
""",
    "observability": """
You are an SRE lead.

Review ONLY observability aspects of the RFC.

Check:
- Metrics
- RED metrics: Rate, Errors, Duration
- Structured logs
- Correlation IDs / trace IDs
- Distributed tracing
- Alert thresholds
- Dashboards
- Runbooks
- Escalation path
- Alert noise control

Return this exact structure:

## Observability Review

### Observability Score
X/10

### Key Findings
- ...

### Critical Gaps
- ...

### Recommendations
- ...

### Evidence From Standards
- ...
""",
}


def run_specialist(
    specialist_type: str,
    rfc_text: str,
    context_docs: List[Document],
) -> Dict[str, str]:
    """
    Runs one specialist agent against the RFC and retrieved standards.
    """

    if specialist_type not in SPECIALIST_PROMPTS:
        return {
            "specialist": specialist_type,
            "status": "ERROR",
            "review": f"Unknown specialist type: {specialist_type}",
        }

    if not context_docs:
        return {
            "specialist": specialist_type,
            "status": "NO_CONTEXT",
            "review": "No standards context available. Flag for human architect review.",
        }

    llm = make_llm()
    standards_context = format_retrieved_docs(context_docs)

    system_prompt = SPECIALIST_PROMPTS[specialist_type]

    user_prompt = f"""
## Retrieved Standards Context

{standards_context}

## RFC Under Review

{rfc_text}

## Instructions

Review only your assigned domain.
Use only the retrieved standards context.
Do not invent enterprise standards.
Cite evidence from the retrieved standards wherever possible.
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    clean_review = output_guard(response.content)

    print(f"[SPECIALIST] {specialist_type} review complete")

    return {
        "specialist": specialist_type,
        "status": "OK",
        "review": clean_review,
    }


def run_all_specialists(
    rfc_text: str,
    context_docs: List[Document],
) -> Dict[str, Dict[str, str]]:
    """
    Runs all MVP specialist agents.
    """
    results = {}

    for specialist in ["security", "scalability", "observability"]:
        results[specialist] = run_specialist(
            specialist_type=specialist,
            rfc_text=rfc_text,
            context_docs=context_docs,
        )

    return results


def merge_specialist_reviews(
    specialist_results: Dict[str, Dict[str, str]]
) -> str:
    """
    Combines specialist reviews into one markdown section.
    """
    sections = ["# Specialist Agent Reviews"]

    for specialist, result in specialist_results.items():
        sections.append(f"\n---\n\n## {specialist.title()} Agent")
        sections.append(f"Status: {result.get('status', 'UNKNOWN')}")
        sections.append(result.get("review", ""))

    return "\n\n".join(sections)