import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.guardrail_agent import input_guard, output_guard
from agents.retrieval_agent import (
    retrieve_with_fallback,
    format_retrieved_docs,
)


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY is missing. Add it to .env in the project root."
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.2,
)


def load_prompt(path: str) -> str:
    """
    Loads a prompt file from disk.
    """
    return Path(path).read_text(encoding="utf-8")


def review_rfc(
    rfc_text: str,
    retrieved_docs: List[Document],
    retrieval_status: str = "OK",
    stream: bool = False,
) -> str:
    """
    Main RFC review function.

    Flow:
    1. Input guard.
    2. Build prompt using retrieved standards.
    3. Call Gemini.
    4. Output guard.
    5. Return markdown review report.
    """

    guard = input_guard(rfc_text)

    if not guard["safe"]:
        return f"⛔ **Review Blocked:** {guard['reason']}"

    if retrieval_status == "NO_CONTEXT" or not retrieved_docs:
        return (
            "⚠️ **Insufficient Standards Context**\n\n"
            "Could not retrieve relevant standards for this RFC. "
            "Flagging for human architect review."
        )

    system_prompt = load_prompt("prompts/system_prompt.txt")
    checklist = load_prompt("prompts/review_checklist.txt")
    user_template = load_prompt("prompts/user_prompt_template.txt")

    retrieved_context = format_retrieved_docs(retrieved_docs)

    user_prompt = user_template.format(
        retrieved_context=retrieved_context,
        checklist=checklist,
        rfc_text=rfc_text,
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    if stream:
        full_response = ""

        for chunk in llm.stream(messages):
            if chunk.content:
                full_response += chunk.content

        response_text = full_response
    else:
        response = llm.invoke(messages)
        response_text = response.content

    clean_response = output_guard(response_text)

    print(f"[REVIEW] Complete — {len(clean_response)} chars output")
    return clean_response


def review_rfc_file(file_path: str) -> dict:
    """
    End-to-end helper:
    1. Reads RFC file.
    2. Retrieves relevant standards.
    3. Generates review report.
    """
    rfc_text = Path(file_path).read_text(encoding="utf-8")

    retrieval_query = f"""
    Review this RFC for security, scalability, reliability, observability,
    rollback, dependencies, cost, and operational readiness.

    RFC excerpt:
    {rfc_text[:1500]}
    """

    retrieved_docs, retrieval_status = retrieve_with_fallback(
        retrieval_query,
        use_hyde=False,
        top_k=5,
    )

    review_report = review_rfc(
        rfc_text=rfc_text,
        retrieved_docs=retrieved_docs,
        retrieval_status=retrieval_status,
    )

    return {
        "file_path": file_path,
        "retrieval_status": retrieval_status,
        "retrieved_docs_count": len(retrieved_docs),
        "retrieved_sources": [
            {
                "source": doc.metadata.get("source", "unknown"),
                "chunk_id": doc.metadata.get("chunk_id", "unknown"),
            }
            for doc in retrieved_docs
        ],
        "review_report": review_report,
    }


if __name__ == "__main__":
    result = review_rfc_file(
        "sample_rfcs/customer_notification_service_rfc.md"
    )

    print("\nRetrieval Status")
    print("----------------")
    print(result["retrieval_status"])

    print("\nRetrieved Sources")
    print("-----------------")
    for source in result["retrieved_sources"]:
        print(source)

    print("\nRFC Review Report")
    print("-----------------")
    print(result["review_report"])