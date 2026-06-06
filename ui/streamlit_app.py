import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Allow imports from project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from agents.ingest_agent import seed_standards
from agents.review_agent import review_rfc_file
from agents.retrieval_agent import retrieve_with_fallback, format_retrieved_docs
from agents.category_retrieval_agent import (
    retrieve_by_category,
    format_category_retrieval_summary,
    format_category_retrieved_docs,
)
from agents.demo_review_generator import generate_demo_review
from agents.demo_specialist_generator import (
    run_demo_specialists,
    merge_demo_specialist_reviews,
)
from agents.rubric_agent import evaluate_rfc_with_rubric
from agents.specialist_agents import run_all_specialists, merge_specialist_reviews
from agents.supervisor_agent import (
    decide_final_recommendation,
    format_supervisor_summary,
)


load_dotenv()

SAMPLE_RFC_PATH = "sample_rfcs/customer_notification_service_rfc.md"


def is_demo_mode() -> bool:
    """
    DEMO_MODE=true means:
    - Do not call Gemini for the main review report.
    - Use local rule-based fallback review.
    """
    return os.getenv("DEMO_MODE", "false").lower() == "true"


def load_sample_rfc() -> str:
    """
    Loads the sample RFC used for demo.
    """
    path = Path(SAMPLE_RFC_PATH)

    if not path.exists():
        return ""

    return path.read_text(encoding="utf-8")


def save_temp_rfc(rfc_text: str) -> str:
    """
    Saves pasted RFC text as a temporary markdown file for the review pipeline.
    """
    temp_path = Path("sample_rfcs/temp_streamlit_rfc.md")
    temp_path.parent.mkdir(exist_ok=True)
    temp_path.write_text(rfc_text, encoding="utf-8")
    return str(temp_path)


def build_result_from_demo_review(
    review_report: str,
    retrieval_status: str,
    retrieved_docs: list,
) -> dict:
    """
    Builds the same result shape as review_rfc_file()
    so the UI can remain unchanged.
    """
    return {
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


st.set_page_config(
    page_title="ArchReviewAI",
    page_icon="🏗️",
    layout="wide",
)

demo_mode = is_demo_mode()

st.title("🏗️ ArchReviewAI")
st.markdown("### Agentic RAG Copilot for Enterprise RFC Reviews")

st.info(
    "ArchReviewAI performs a first-pass architecture review of RFCs/design documents "
    "using enterprise standards. The goal is to improve RFC quality before senior architect review."
)


with st.sidebar:
    st.header("System Status")

    if demo_mode:
        st.success("Mode: Demo-safe local review")
        st.caption("No external LLM call is made for the main review report.")
    else:
        st.success("LLM: Gemini live mode")

    st.success("Vector DB: ChromaDB")
    st.success("RAG: Category-wise standards retrieval")
    st.success("Rubric: Deterministic scoring")
    st.success("Agents: Security, Scalability, Observability")
    st.success("Supervisor: Final decision layer")

    st.info(
        "Flow: RFC → Category Retrieval → Rubric Score → Specialist Agents "
        "→ Supervisor Decision → Review Report"
    )

    if st.button("🌱 Seed / Refresh Standards KB"):
        with st.spinner("Seeding standards into ChromaDB..."):
            seed_standards()
        st.success("Standards knowledge base refreshed.")


tab_review, tab_evidence, tab_arch = st.tabs(
    [
        "1. RFC Review Demo",
        "2. RAG Evidence",
        "3. Architecture View",
    ]
)


with tab_review:
    st.header("RFC Review Demo")

    if demo_mode:
        st.warning(
            "Demo Mode is ON. The main review report and specialist reviews are generated locally without calling Gemini."
        )
    else:
        st.info("Live Mode is ON. Gemini will be used for live LLM reviews.")

    default_rfc = load_sample_rfc()

    rfc_text = st.text_area(
        "Paste RFC / Design Document",
        value=default_rfc,
        height=420,
    )

    if st.button("🚀 Run Review", type="primary"):
        if not rfc_text.strip():
            st.error("Please paste an RFC before running the review.")
        else:
            with st.spinner("Running ArchReviewAI review..."):
                temp_file_path = save_temp_rfc(rfc_text)

                # 1. Deterministic scoring.
                rubric_result = evaluate_rfc_with_rubric(rfc_text)

                # 2. Category-wise retrieval for balanced RAG grounding.
                category_retrieval_result = retrieve_by_category(
                    top_k_per_category=2,
                    use_hyde=False,
                )

                specialist_docs = category_retrieval_result["all_unique_docs"]
                specialist_retrieval_status = (
                    "Category-wise retrieval: "
                    f"{category_retrieval_result['total_unique_chunks']} unique chunks"
                )

                category_retrieval_summary = format_category_retrieval_summary(
                    category_retrieval_result
                )

                # 3. Generate main review report.
                if demo_mode:
                    review_report = generate_demo_review(
                        rfc_text=rfc_text,
                        rubric_result=rubric_result,
                        retrieved_docs=specialist_docs,
                    )

                    result = build_result_from_demo_review(
                        review_report=review_report,
                        retrieval_status=specialist_retrieval_status,
                        retrieved_docs=specialist_docs,
                    )
                else:
                    result = review_rfc_file(temp_file_path)

                # 4. Run specialist agents.
                if demo_mode:
                    specialist_results = run_demo_specialists(rubric_result)
                    specialist_report = merge_demo_specialist_reviews(
                        specialist_results
                    )
                else:
                    try:
                        specialist_results = run_all_specialists(
                            rfc_text=rfc_text,
                            context_docs=specialist_docs,
                        )
                        specialist_report = merge_specialist_reviews(
                            specialist_results
                        )
                    except Exception as error:
                        specialist_results = {
                            "specialist_fallback": {
                                "status": "FALLBACK",
                                "review": (
                                    "Specialist agent live review was skipped or failed. "
                                    f"Reason: {error}"
                                ),
                            }
                        }

                        specialist_report = (
                            "# Specialist Agent Reviews\n\n"
                            "Specialist live review was not available in this run.\n\n"
                            "Use the deterministic rubric result and retrieved standards evidence "
                            "for demo-safe review."
                        )

                # 5. Supervisor final recommendation.
                supervisor_result = decide_final_recommendation(
                    rubric_result=rubric_result,
                    specialist_results=specialist_results,
                )

                supervisor_summary = format_supervisor_summary(supervisor_result)

            st.subheader("Review Summary")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Retrieval Status", result["retrieval_status"])

            with col2:
                st.metric("Retrieved Standards", result["retrieved_docs_count"])

            with col3:
                st.metric("Rubric Score", rubric_result["rubric_score"])

            with col4:
                st.metric("Final Decision", supervisor_result["final_decision"])

            st.subheader("Supervisor Final Recommendation")
            st.markdown(supervisor_summary)

            st.subheader("Deterministic Rubric Result")
            st.json(rubric_result)

            st.subheader("RFC Review Report")
            st.markdown(result["review_report"])

            st.subheader("Specialist Agent Reviews")
            st.markdown(specialist_report)

            st.download_button(
                label="⬇️ Download General Review Report",
                data=result["review_report"],
                file_name="archreviewai_rfc_review_report.md",
                mime="text/markdown",
            )

            st.download_button(
                label="⬇️ Download Specialist Review Report",
                data=specialist_report,
                file_name="archreviewai_specialist_review_report.md",
                mime="text/markdown",
            )

            with st.expander("Retrieved Sources Used by Main Review"):
                st.json(result["retrieved_sources"])

            with st.expander("Specialist Agent Retrieval Status"):
                st.write(specialist_retrieval_status)

            with st.expander("Category-wise Retrieval Summary"):
                st.markdown(category_retrieval_summary)

            with st.expander("Raw Supervisor Result"):
                st.json(supervisor_result)

            with st.expander("Raw Specialist Results"):
                st.json(specialist_results)


with tab_evidence:
    st.header("RAG Evidence Explorer")

    st.text_input(
        "Reference query",
        value=(
            "What security, observability, scalability, rollback, "
            "and cost requirements must an RFC include?"
        ),
        disabled=True,
    )

    st.caption(
        "Phase 2 uses fixed category-wise retrieval instead of one broad query. "
        "This gives balanced context across RFC template, security, scalability, reliability, observability, rollback, and operations."
    )

    if st.button("🔍 Retrieve Standards"):
        with st.spinner("Searching ChromaDB standards knowledge base category-wise..."):
            category_retrieval_result = retrieve_by_category(
                top_k_per_category=2,
                use_hyde=False,
            )

            docs = category_retrieval_result["all_unique_docs"]
            status = (
                "Category-wise retrieval completed: "
                f"{category_retrieval_result['total_unique_chunks']} unique chunks"
            )

        st.subheader("Retrieval Status")
        st.write(status)

        st.subheader("Category-wise Retrieval Summary")
        st.markdown(format_category_retrieval_summary(category_retrieval_result))

        st.subheader("Retrieved Standards Chunks")

        seen = set()
        display_index = 1

        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            chunk_id = doc.metadata.get("chunk_id", "unknown")
            dedupe_key = f"{source}:{chunk_id}"

            if dedupe_key in seen:
                continue

            seen.add(dedupe_key)

            st.markdown(f"### {display_index}. {source} — chunk `{chunk_id}`")
            st.write(doc.page_content)

            display_index += 1

        with st.expander("Formatted Context Sent to LLM / Review Generator"):
            st.text(format_category_retrieved_docs(category_retrieval_result))


with tab_arch:
    st.header("Architecture View")

    architecture_flow = (
        "Engineer RFC / Design Doc\n"
        "        ↓\n"
        "Input Guard\n"
        "        ↓\n"
        "Category-wise RAG Retrieval over Enterprise Standards\n"
        "        ↓\n"
        "Balanced Standards Context\n"
        "        ↓\n"
        "Deterministic Rubric Scoring\n"
        "        ↓\n"
        "Specialist Agents\n"
        "  ├── Security Agent\n"
        "  ├── Scalability / Reliability Agent\n"
        "  └── Observability Agent\n"
        "        ↓\n"
        "Supervisor Decision Layer\n"
        "        ↓\n"
        "Review Report Generator\n"
        "  ├── Demo Mode: Local rule-based report\n"
        "  └── Live Mode: Gemini review report\n"
        "        ↓\n"
        "Output Guard\n"
        "        ↓\n"
        "Final Review Report\n"
        "        ↓\n"
        "Recommendation: APPROVE / NEEDS_REVISION / ARCHITECT_REVIEW"
    )

    st.code(architecture_flow, language="text")

    st.subheader("Current MVP Components")

    st.markdown("- **Standards knowledge base:** Security, scalability, observability, cost, rollback.")
    st.markdown("- **Chunking:** Standards are split into searchable chunks.")
    st.markdown("- **Embeddings:** Text is converted into semantic vectors.")
    st.markdown("- **Vector DB:** ChromaDB stores searchable standards.")
    st.markdown("- **Retrieval:** Category-wise retrieval gives balanced standards context.")
    st.markdown("- **Rubric:** Rule-based scoring and decisioning.")
    st.markdown("- **Specialist agents:** Security, scalability/reliability, and observability.")
    st.markdown("- **Supervisor:** Consolidates rubric and specialist outputs into a final decision.")
    st.markdown("- **Review generator:** Supports demo-safe local mode and live Gemini mode.")
    st.markdown("- **UI:** Streamlit provides a leadership-friendly demo.")

    st.subheader("Key Design Principle")

    st.info(
        "The LLM explains the gaps when live mode is available. "
        "The deterministic rubric calculates the score. "
        "The supervisor decides the final recommendation. "
        "Category-wise retrieval improves RAG grounding quality. "
        "Demo mode keeps the app runnable without external LLM dependency."
    )

    st.subheader("Next Planned Components")

    st.markdown("- Retrieval quality tests.")
    st.markdown("- Hybrid keyword + vector search.")
    st.markdown("- Reranking.")
    st.markdown("- LangGraph workflow.")
    st.markdown("- LangSmith observability.")
    st.markdown("- RAGAS evaluation.")
    st.markdown("- Retrieval quality metrics: Recall@K, Precision@K, MRR.")
    st.markdown("- Day 3 extensions: n8n, MCP, Graph RAG, FastAPI, Docker.")