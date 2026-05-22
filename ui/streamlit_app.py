import os
import sys
from pathlib import Path
from agents.rubric_agent import evaluate_rfc_with_rubric
import streamlit as st
from dotenv import load_dotenv

# Allow imports from project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from agents.ingest_agent import seed_standards
from agents.review_agent import review_rfc_file
from agents.retrieval_agent import retrieve_with_fallback, format_retrieved_docs


load_dotenv()

SAMPLE_RFC_PATH = "sample_rfcs/customer_notification_service_rfc.md"


def load_sample_rfc() -> str:
    path = Path(SAMPLE_RFC_PATH)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def save_temp_rfc(rfc_text: str) -> str:
    temp_path = Path("sample_rfcs/temp_streamlit_rfc.md")
    temp_path.parent.mkdir(exist_ok=True)
    temp_path.write_text(rfc_text, encoding="utf-8")
    return str(temp_path)


st.set_page_config(
    page_title="ArchReviewAI",
    page_icon="🏗️",
    layout="wide",
)

st.title("🏗️ ArchReviewAI")
st.markdown("### Agentic RAG Copilot for Enterprise RFC Reviews")

st.info(
    "ArchReviewAI performs a first-pass architecture review of RFCs/design documents "
    "using enterprise standards. The goal is to improve RFC quality before senior architect review."
)

with st.sidebar:
    st.header("System Status")
    st.success("LLM: Gemini")
    st.success("Vector DB: ChromaDB")
    st.success("RAG: Standards-grounded retrieval")
    st.info("Flow: RFC → Retrieve Standards → Generate Review")

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
                result = review_rfc_file(temp_file_path)
                rubric_result = evaluate_rfc_with_rubric(rfc_text)

            st.subheader("Review Summary")

                        c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric("Retrieval Status", result["retrieval_status"])

            with c2:
                st.metric("Retrieved Standards", result["retrieved_docs_count"])

            with c3:
                st.metric("Rubric Score", rubric_result["rubric_score"])

            with c4:
                st.metric("Decision", rubric_result["decision"])

            st.subheader("Deterministic Rubric Result")
            st.json(rubric_result)
            st.markdown(result["review_report"])

            st.download_button(
                label="⬇️ Download Review Report",
                data=result["review_report"],
                file_name="archreviewai_rfc_review_report.md",
                mime="text/markdown",
            )

            with st.expander("Retrieved Sources Used"):
                st.json(result["retrieved_sources"])


with tab_evidence:
    st.header("RAG Evidence Explorer")

    query = st.text_input(
        "Ask what standards are relevant",
        value="What security, observability, scalability, rollback, and cost requirements must an RFC include?",
    )

    if st.button("🔍 Retrieve Standards"):
        with st.spinner("Searching ChromaDB standards knowledge base..."):
            docs, status = retrieve_with_fallback(
                query=query,
                use_hyde=False,
                top_k=5,
            )

        st.subheader("Retrieval Status")
        st.write(status)

        st.subheader("Retrieved Standards Chunks")

        for index, doc in enumerate(docs, start=1):
            source = doc.metadata.get("source", "unknown")
            chunk_id = doc.metadata.get("chunk_id", "unknown")

            st.markdown(f"### {index}. {source} — chunk `{chunk_id}`")
            st.write(doc.page_content)

        with st.expander("Formatted Context Sent to LLM"):
            st.text(format_retrieved_docs(docs))


with tab_arch:
    st.header("Architecture View")

    architecture_flow = (
        "Engineer RFC / Design Doc\n"
        "        ↓\n"
        "Input Guard\n"
        "        ↓\n"
        "RAG Retrieval over Enterprise Standards\n"
        "        ↓\n"
        "Relevant Standards Context\n"
        "        ↓\n"
        "Gemini Review Agent\n"
        "        ↓\n"
        "Output Guard\n"
        "        ↓\n"
        "Review Report\n"
        "        ↓\n"
        "Recommendation: APPROVE / NEEDS_REVISION / ARCHITECT_REVIEW"
    )

    st.code(architecture_flow, language="text")

    st.subheader("Current MVP Components")

    st.markdown("- **Standards knowledge base:** Security, scalability, observability, cost, rollback.")
    st.markdown("- **Chunking:** Standards are split into searchable chunks.")
    st.markdown("- **Embeddings:** Text is converted into semantic vectors.")
    st.markdown("- **Vector DB:** ChromaDB stores searchable standards.")
    st.markdown("- **Retrieval:** Relevant standards are retrieved for each RFC.")
    st.markdown("- **Review Agent:** Gemini generates the structured RFC review.")
    st.markdown("- **UI:** Streamlit provides a leadership-friendly demo.")

    st.subheader("Next Planned Components")

    st.markdown("- Specialist agents: Security, scalability, observability.")
    st.markdown("- Supervisor recommendation.")
    st.markdown("- LangGraph workflow.")
    st.markdown("- LangSmith observability.")
    st.markdown("- RAGAS evaluation.")
    st.markdown("- Day 3 extensions: n8n, MCP, Graph RAG, FastAPI, Docker.")