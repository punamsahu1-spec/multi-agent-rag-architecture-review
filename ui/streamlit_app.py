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
from agents.category_retrieval_agent import (
    retrieve_by_category,
    format_category_retrieval_summary,
    format_category_retrieved_docs,
    calculate_retrieval_coverage,
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
    return os.getenv("DEMO_MODE", "false").lower() == "true"


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


def build_result_from_demo_review(
    review_report: str,
    retrieval_status: str,
    retrieved_docs: list,
) -> dict:
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
    st.success("Orchestration: Lightweight crew-style flow")
    st.success("Evaluation: Basic quality gates")
    st.success("Governance: Human review + audit-friendly flow")

    st.info(
        "Flow: RFC → Category Retrieval → Rubric Score → Specialist Agents "
        "→ Supervisor Decision → Human Review Routing → Quality Gates → Review Report"
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

                rubric_result = evaluate_rfc_with_rubric(rfc_text)

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

                retrieval_coverage = calculate_retrieval_coverage(
                    category_retrieval_result
                )

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

                supervisor_result = decide_final_recommendation(
                    rubric_result=rubric_result,
                    specialist_results=specialist_results,
                )

                supervisor_summary = format_supervisor_summary(supervisor_result)

                workflow_state = {
                    "Input received": "Yes" if rfc_text.strip() else "No",
                    "Retrieval complete": "Yes",
                    "Retrieved unique chunks": category_retrieval_result[
                        "total_unique_chunks"
                    ],
                    "RAG coverage": f"{retrieval_coverage['coverage_percent']}%",
                    "Rubric complete": "Yes",
                    "Rubric score": rubric_result["rubric_score"],
                    "Specialist review complete": "Yes",
                    "Supervisor decision": supervisor_result["final_decision"],
                    "Human review required": supervisor_result[
                        "human_review_required"
                    ],
                    "Report generated": "Yes",
                }

                agent_trace = [
                    {
                        "Agent": "Category Retriever",
                        "Action": (
                            f"Retrieved {category_retrieval_result['total_unique_chunks']} "
                            "unique chunks across review categories"
                        ),
                    },
                    {
                        "Agent": "Rubric Agent",
                        "Action": (
                            f"Calculated readiness score: "
                            f"{rubric_result['rubric_score']}"
                        ),
                    },
                    {
                        "Agent": "Specialist Agents",
                        "Action": "Completed domain-specific review",
                    },
                    {
                        "Agent": "Supervisor Agent",
                        "Action": (
                            f"Final decision: "
                            f"{supervisor_result['final_decision']}"
                        ),
                    },
                    {
                        "Agent": "Human Review Router",
                        "Action": (
                            f"Human review required: "
                            f"{supervisor_result['human_review_required']}"
                        ),
                    },
                    {
                        "Agent": "Report Generator",
                        "Action": "Generated final RFC review report",
                    },
                ]

                agent_roles = [
                    {
                        "Role": "Security Reviewer",
                        "Responsibility": (
                            "Checks authentication, authorization, PII, encryption, "
                            "secrets, and audit logging."
                        ),
                    },
                    {
                        "Role": "Scalability / Reliability Reviewer",
                        "Responsibility": (
                            "Checks RPS, peak load, scaling strategy, timeout, retry, "
                            "DLQ, idempotency, DR, and backup."
                        ),
                    },
                    {
                        "Role": "Observability Reviewer",
                        "Responsibility": (
                            "Checks metrics, logs, tracing, alerts, dashboards, "
                            "runbooks, and escalation path."
                        ),
                    },
                    {
                        "Role": "Supervisor / Lead Architect",
                        "Responsibility": (
                            "Consolidates rubric and specialist outputs into APPROVE, "
                            "NEEDS_REVISION, or ARCHITECT_REVIEW."
                        ),
                    },
                ]

                orchestration_summary = {
                    "Mode": "Simple Python orchestration",
                    "Pattern": "Specialist agents + supervisor",
                    "Task flow": (
                        "RFC received → category retrieval → rubric scoring → "
                        "specialist reviews → supervisor consolidation → "
                        "human review routing → report generation"
                    ),
                    "Why this matters": (
                        "This keeps the workflow explainable before introducing "
                        "heavier frameworks such as CrewAI, AutoGen, or LangGraph."
                    ),
                }

                evaluation_summary = {
                    "Retrieval coverage": f"{retrieval_coverage['coverage_percent']}%",
                    "Rubric score": rubric_result["rubric_score"],
                    "Final decision": supervisor_result["final_decision"],
                    "Human review required": supervisor_result["human_review_required"],
                    "Report generated": "Yes",
                }

                observability_trace = [
                    {
                        "Step": "Input Guard",
                        "Status": "Completed",
                        "Output": "RFC text accepted",
                    },
                    {
                        "Step": "Category Retriever",
                        "Status": "Completed",
                        "Output": (
                            f"{category_retrieval_result['total_unique_chunks']} "
                            "unique chunks retrieved"
                        ),
                    },
                    {
                        "Step": "Rubric Agent",
                        "Status": "Completed",
                        "Output": f"Score {rubric_result['rubric_score']}",
                    },
                    {
                        "Step": "Specialist Agents",
                        "Status": "Completed",
                        "Output": "Domain reviews completed",
                    },
                    {
                        "Step": "Supervisor Agent",
                        "Status": "Completed",
                        "Output": supervisor_result["final_decision"],
                    },
                    {
                        "Step": "Human Review Router",
                        "Status": "Completed",
                        "Output": (
                            f"Human review: "
                            f"{supervisor_result['human_review_required']}"
                        ),
                    },
                    {
                        "Step": "Report Generator",
                        "Status": "Completed",
                        "Output": "Review report generated",
                    },
                ]

                quality_gates = [
                    {
                        "Gate": "RAG coverage available",
                        "Result": (
                            "PASS"
                            if retrieval_coverage["coverage_percent"] > 0
                            else "WARN"
                        ),
                    },
                    {
                        "Gate": "Rubric score available",
                        "Result": (
                            "PASS" if rubric_result.get("rubric_score") else "WARN"
                        ),
                    },
                    {
                        "Gate": "Supervisor decision available",
                        "Result": (
                            "PASS"
                            if supervisor_result.get("final_decision")
                            else "WARN"
                        ),
                    },
                    {
                        "Gate": "Human review routing available",
                        "Result": (
                            "PASS"
                            if supervisor_result.get("human_review_required")
                            else "WARN"
                        ),
                    },
                    {
                        "Gate": "Report generated",
                        "Result": "PASS" if result.get("review_report") else "WARN",
                    },
                ]

            st.subheader("Review Summary")

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric("Retrieval Status", result["retrieval_status"])

            with col2:
                st.metric("Retrieved Standards", result["retrieved_docs_count"])

            with col3:
                st.metric("Rubric Score", rubric_result["rubric_score"])

            with col4:
                st.metric("Final Decision", supervisor_result["final_decision"])

            with col5:
                st.metric("RAG Coverage", f"{retrieval_coverage['coverage_percent']}%")

            st.subheader("Supervisor Final Recommendation")
            st.markdown(supervisor_summary)

            st.subheader("Human Review Routing")

            if supervisor_result["human_review_required"] == "YES":
                st.error("Human Review Required: YES")
            else:
                st.success("Human Review Required: NO")

            st.write(supervisor_result["reason"])

            st.subheader("Workflow State")
            st.json(workflow_state)

            st.subheader("Agent Trace")
            st.table(agent_trace)

            st.subheader("Agent Roles")
            st.table(agent_roles)

            st.subheader("Orchestration Summary")
            st.json(orchestration_summary)

            st.subheader("Evaluation Summary")
            st.json(evaluation_summary)

            st.subheader("Observability Trace")
            st.table(observability_trace)

            st.subheader("Quality Gates")
            st.table(quality_gates)

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

            with st.expander("Retrieval Coverage"):
                st.json(retrieval_coverage)

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
        "This gives balanced context across RFC template, security, scalability, "
        "reliability, observability, rollback, and operations."
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

            retrieval_coverage = calculate_retrieval_coverage(
                category_retrieval_result
            )

        st.subheader("Retrieval Status")
        st.write(status)

        st.metric("RAG Coverage", f"{retrieval_coverage['coverage_percent']}%")

        st.subheader("Category-wise Retrieval Summary")
        st.markdown(format_category_retrieval_summary(category_retrieval_result))

        with st.expander("Retrieval Coverage Details"):
            st.json(retrieval_coverage)

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
        "Category Retriever Agent\n"
        "        ↓\n"
        "Balanced Standards Context\n"
        "        ↓\n"
        "Rubric Agent\n"
        "        ↓\n"
        "Specialist Agents\n"
        "  ├── Security Agent\n"
        "  ├── Scalability / Reliability Agent\n"
        "  └── Observability Agent\n"
        "        ↓\n"
        "Supervisor Agent\n"
        "        ↓\n"
        "Human Review Routing\n"
        "  ├── APPROVE\n"
        "  ├── NEEDS_REVISION\n"
        "  └── ARCHITECT_REVIEW\n"
        "        ↓\n"
        "Quality Gates / Observability Trace\n"
        "        ↓\n"
        "Review Report Generator\n"
        "  ├── Demo Mode: Local rule-based report\n"
        "  └── Live Mode: Gemini review report\n"
        "        ↓\n"
        "Final Review Report"
    )

    st.code(architecture_flow, language="text")

    st.subheader("Current MVP Components")

    st.markdown(
        "- **Standards knowledge base:** Security, scalability, observability, cost, rollback."
    )
    st.markdown("- **Chunking:** Standards are split into searchable chunks.")
    st.markdown("- **Embeddings:** Text is converted into semantic vectors.")
    st.markdown("- **Vector DB:** ChromaDB stores searchable standards.")
    st.markdown("- **Retrieval:** Category-wise retrieval gives balanced standards context.")
    st.markdown("- **Rubric:** Rule-based scoring and decisioning.")
    st.markdown(
        "- **Specialist agents:** Security, scalability/reliability, and observability."
    )
    st.markdown(
        "- **Supervisor:** Consolidates rubric and specialist outputs into a final decision."
    )
    st.markdown("- **Human Review Routing:** Escalates risky RFCs to human architects.")
    st.markdown("- **Workflow State:** Shows which review steps completed.")
    st.markdown("- **Agent Trace:** Shows what each agent contributed.")
    st.markdown("- **Agent Roles:** Shows specialist responsibilities.")
    st.markdown("- **Orchestration Summary:** Shows lightweight crew-style task flow.")
    st.markdown("- **Evaluation Summary:** Shows key review-quality signals.")
    st.markdown("- **Observability Trace:** Shows workflow step status and outputs.")
    st.markdown("- **Quality Gates:** Shows basic pass/warn checks before trusting output.")
    st.markdown("- **Review generator:** Supports demo-safe local mode and live Gemini mode.")
    st.markdown("- **UI:** Streamlit provides a leadership-friendly demo.")

    st.subheader("Key Design Principle")

    st.info(
        "The LLM explains the gaps when live mode is available. "
        "The deterministic rubric calculates the score. "
        "The supervisor decides the final recommendation. "
        "Human Review Routing escalates risky RFCs. "
        "Workflow State and Agent Trace make the process explainable. "
        "Agent Roles and Orchestration Summary show a lightweight crew-style workflow. "
        "Evaluation Summary, Observability Trace, and Quality Gates make the review measurable. "
        "Demo mode keeps the app runnable without external LLM dependency."
    )

    st.subheader("CrewAI-style Mapping")

    crewai_mapping = [
        {
            "ArchReviewAI Concept": "Security Reviewer",
            "CrewAI-style Concept": "Agent with security architect role",
        },
        {
            "ArchReviewAI Concept": "Scalability / Reliability Reviewer",
            "CrewAI-style Concept": "Agent with distributed systems architect role",
        },
        {
            "ArchReviewAI Concept": "Observability Reviewer",
            "CrewAI-style Concept": "Agent with SRE reviewer role",
        },
        {
            "ArchReviewAI Concept": "Supervisor / Lead Architect",
            "CrewAI-style Concept": "Manager agent that consolidates outputs",
        },
        {
            "ArchReviewAI Concept": "Review dimensions",
            "CrewAI-style Concept": "Tasks assigned to agents",
        },
        {
            "ArchReviewAI Concept": "Architecture review workflow",
            "CrewAI-style Concept": "Crew executing a review process",
        },
    ]

    st.table(crewai_mapping)

    st.subheader("AutoGen-style Mapping")

    autogen_mapping = [
        {
            "ArchReviewAI Concept": "Security Reviewer",
            "AutoGen-style Concept": "Assistant agent focused on security risks",
        },
        {
            "ArchReviewAI Concept": "Scalability / Reliability Reviewer",
            "AutoGen-style Concept": "Assistant agent focused on scale and resilience",
        },
        {
            "ArchReviewAI Concept": "Observability Reviewer",
            "AutoGen-style Concept": "Assistant agent focused on operations visibility",
        },
        {
            "ArchReviewAI Concept": "Supervisor / Lead Architect",
            "AutoGen-style Concept": "Coordinator or critic agent",
        },
        {
            "ArchReviewAI Concept": "Specialist review exchange",
            "AutoGen-style Concept": "Multi-agent conversation",
        },
        {
            "ArchReviewAI Concept": "Final recommendation",
            "AutoGen-style Concept": "Consolidated group output",
        },
    ]

    st.table(autogen_mapping)

    st.subheader("Framework-neutral Design Choice")

    st.info(
        "ArchReviewAI first defines the business workflow and agent responsibilities clearly. "
        "CrewAI, AutoGen, or LangGraph can be added later as orchestration frameworks, "
        "but the architecture does not depend on a specific framework."
    )

    st.subheader("Evaluation and Observability Mapping")

    eval_obs_mapping = [
        {
            "Current ArchReviewAI View": "Agent Trace",
            "Future Tool Mapping": "LangSmith trace",
        },
        {
            "Current ArchReviewAI View": "RAG Coverage",
            "Future Tool Mapping": "RAGAS context recall / context precision",
        },
        {
            "Current ArchReviewAI View": "Quality Gates",
            "Future Tool Mapping": "CI/CD evaluation checks",
        },
        {
            "Current ArchReviewAI View": "Human Review Routing",
            "Future Tool Mapping": "Human-in-the-loop governance workflow",
        },
        {
            "Current ArchReviewAI View": "Retrieved Sources",
            "Future Tool Mapping": "Grounded evidence audit trail",
        },
    ]

    st.table(eval_obs_mapping)

    st.subheader("Enterprise Integration Simulation")

    enterprise_integrations = [
        {
            "Enterprise Tool": "SharePoint / Confluence",
            "ArchReviewAI Use": "Source of enterprise architecture standards.",
            "Current Prototype": "Simulated using local standards_docs folder.",
        },
        {
            "Enterprise Tool": "GitHub / GitLab",
            "ArchReviewAI Use": "Source of RFCs, design docs, pull requests, or ADRs.",
            "Current Prototype": "Simulated using pasted RFC text and sample_rfcs folder.",
        },
        {
            "Enterprise Tool": "Jira",
            "ArchReviewAI Use": "Create revision tasks when RFC needs changes.",
            "Current Prototype": "Simulated through NEEDS_REVISION / ARCHITECT_REVIEW decision.",
        },
        {
            "Enterprise Tool": "Teams / Slack",
            "ArchReviewAI Use": "Notify architects or engineering teams about review outcome.",
            "Current Prototype": "Simulated through Human Review Routing section.",
        },
        {
            "Enterprise Tool": "Review History / Audit Store",
            "ArchReviewAI Use": "Maintain trace of RFC review, evidence, score, and decision.",
            "Current Prototype": "Simulated through Workflow State, Agent Trace, and Quality Gates.",
        },
    ]

    st.table(enterprise_integrations)

    st.info(
        "This prototype uses local files and Streamlit for simplicity. "
        "In an enterprise setup, the same workflow can connect to SharePoint, Confluence, "
        "GitHub, Jira, Teams, Slack, and audit stores."
    )

    st.subheader("Governance and Risk Controls")

    governance_controls = [
        {
            "Governance Area": "Policy grounding",
            "How ArchReviewAI handles it": "Uses RAG over enterprise standards instead of relying only on generic model memory.",
            "Current implementation": "Category-wise retrieval from standards_docs.",
        },
        {
            "Governance Area": "Human oversight",
            "How ArchReviewAI handles it": "Routes risky or incomplete RFCs to human architects.",
            "Current implementation": "Human Review Routing with APPROVE / NEEDS_REVISION / ARCHITECT_REVIEW.",
        },
        {
            "Governance Area": "Auditability",
            "How ArchReviewAI handles it": "Shows workflow state, agent trace, retrieved sources, and quality gates.",
            "Current implementation": "Workflow State, Agent Trace, RAG Evidence, Quality Gates.",
        },
        {
            "Governance Area": "Safe demo execution",
            "How ArchReviewAI handles it": "Supports demo mode without external LLM calls.",
            "Current implementation": "DEMO_MODE=true local rule-based review.",
        },
        {
            "Governance Area": "Sensitive data awareness",
            "How ArchReviewAI handles it": "Highlights the need for PII, secrets, encryption, and access-control checks.",
            "Current implementation": "Security rubric and Security Reviewer.",
        },
        {
            "Governance Area": "Quality control",
            "How ArchReviewAI handles it": "Uses quality gates before trusting the review output.",
            "Current implementation": "PASS/WARN quality gate table.",
        },
    ]

    st.table(governance_controls)

    st.info(
        "This section shows that ArchReviewAI is designed as a governed review workflow, "
        "not just a text-generation demo."
    )

    st.subheader("Next Planned Components")

    st.markdown("- Optional actual CrewAI / AutoGen implementation.")
    st.markdown("- LangGraph workflow.")
    st.markdown("- Hybrid keyword + vector search.")
    st.markdown("- Reranking.")
    st.markdown("- LangSmith observability.")
    st.markdown("- RAGAS evaluation.")
    st.markdown("- Retrieval quality metrics: Recall@K, Precision@K, MRR.")
    st.markdown("- Production packaging and README refresh.")