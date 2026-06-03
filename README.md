# ArchReviewAI — Agentic RAG Copilot for Enterprise RFC Reviews

ArchReviewAI is a hands-on GenAI architecture project that demonstrates how an enterprise RFC/design-document review assistant can be built using RAG, vector search, LLM review generation, deterministic scoring, Streamlit UI, and supervisor-style decisioning.

The goal is to help engineering teams improve architecture proposals before senior architect review by checking for missing security, scalability, reliability, observability, rollback, cost, and operational-readiness details.

---

## 1. Problem Statement

In large engineering organizations, RFCs and design documents often wait for senior architect review. Many submissions miss important non-functional requirements such as security, scalability, reliability, observability, rollback, cost, and support ownership.

This creates several problems:

* Senior architects become review bottlenecks.
* RFC quality varies across teams.
* Repeated review comments slow down delivery.
* Security and operational risks are found late.
* Architecture review decisions are inconsistent.

ArchReviewAI provides a first-pass AI-assisted architecture review so engineers can improve RFC quality before formal architect approval.

---

## 2. What ArchReviewAI Does

ArchReviewAI reviews an RFC/design document against enterprise architecture standards.

Current workflow:

```text
Engineer RFC / Design Document
        ↓
Input Guard
        ↓
RAG Retrieval over Enterprise Standards
        ↓
Relevant Standards Context
        ↓
Deterministic Rubric Scoring
        ↓
LLM Review Agent
        ↓
Supervisor-style Recommendation
        ↓
Review Report
        ↓
APPROVE / NEEDS_REVISION / ARCHITECT_REVIEW
```

---

## 3. Current Implementation Status

This is a working MVP/prototype. It is not yet production-grade, but it demonstrates the core GenAI architecture pattern.

### Implemented Now

* Enterprise standards knowledge base.
* RFC template standard.
* Security checklist.
* Scalability and reliability standard.
* Observability standard.
* Cost and operational readiness checklist.
* Document ingestion and chunking.
* Gemini embeddings.
* ChromaDB vector store.
* RAG retrieval over standards.
* MMR-based retrieval.
* Optional HyDE-style query expansion.
* Prompt files for structured RFC review.
* Gemini-based RFC review generation.
* Deterministic architecture-readiness rubric.
* Streamlit UI with three tabs:

  * RFC Review Demo.
  * RAG Evidence Explorer.
  * Architecture View.
* Sample RFC for Customer Notification Service.
* Basic guardrail layer.
* Supervisor-style final recommendation.
* Downloadable review report.

---

## 4. Key Components

### 4.1 Standards Knowledge Base

Folder:

```text
standards_docs/
```

Contains enterprise review standards:

```text
rfc_template_standard.md
security_checklist.md
scalability_reliability_standard.md
observability_standard.md
cost_operational_readiness.md
```

These documents act as the review rulebook.

---

### 4.2 Ingest Agent

File:

```text
agents/ingest_agent.py
```

Responsibilities:

* Load standards documents.
* Split them into smaller chunks.
* Generate embeddings.
* Store chunks in ChromaDB.

Flow:

```text
standards_docs/*.md
        ↓
load documents
        ↓
chunk documents
        ↓
create embeddings
        ↓
store in ChromaDB
```

---

### 4.3 Retrieval Agent

File:

```text
agents/retrieval_agent.py
```

Responsibilities:

* Search ChromaDB for relevant standards.
* Retrieve top-k context chunks.
* Use MMR to balance relevance and diversity.
* Format retrieved context for the LLM.

Example:

```text
Query: What observability requirements should an RFC include?

Retrieved context:
- Metrics
- Logs
- Tracing
- Alert thresholds
- Dashboards
- Runbooks
```

---

### 4.4 Review Agent

File:

```text
agents/review_agent.py
```

Responsibilities:

* Accept RFC text.
* Retrieve relevant standards.
* Build system/user prompt.
* Generate structured review using Gemini.
* Return markdown review report.

The review report includes:

* Overall score.
* Approval status.
* Executive summary.
* Section completeness.
* Critical issues.
* Evidence from standards.
* Recommended next steps.
* Human review recommendation.

---

### 4.5 Deterministic Rubric Agent

File:

```text
agents/rubric_agent.py
```

Purpose:

The LLM explains gaps, but the rubric calculates the score.

Rubric logic:

```text
Start score = 10

PASS     = no deduction
PARTIAL  = -1
MISSING  = -2
```

Dimensions evaluated:

* Security.
* Scalability.
* Reliability.
* Observability.
* Rollback.
* Cost and operations.

Final decision:

```text
APPROVE
NEEDS_REVISION
ARCHITECT_REVIEW
```

---

### 4.6 Streamlit UI

File:

```text
ui/streamlit_app.py
```

The UI provides a leadership-friendly demo.

Tabs:

```text
1. RFC Review Demo
2. RAG Evidence
3. Architecture View
```

The UI allows users to:

* Paste or edit an RFC.
* Run review.
* See retrieval status.
* See rubric score.
* See final decision.
* See RAG evidence.
* Download the generated review report.

---

## 5. Sample Use Case

Sample RFC:

```text
sample_rfcs/customer_notification_service_rfc.md
```

The sample RFC describes a Customer Notification Service using:

* REST APIs.
* Kafka.
* PostgreSQL.
* External SMS provider.
* Retry logic.
* Logs.
* Rollback.

It intentionally has gaps in:

* Authentication.
* Authorization.
* PII handling.
* Secrets management.
* RPS and peak load.
* SLOs.
* DLQ and idempotency.
* Metrics and tracing.
* Alerting and runbooks.
* Cost and support ownership.

This helps demonstrate how ArchReviewAI identifies architecture-readiness gaps.

---

## 6. How to Run

### Step 1: Create virtual environment

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
```

### Step 2: Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 3: Add environment variables

Create `.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key
LANGCHAIN_API_KEY=your_langsmith_key_optional
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=archreviewai-rfc-agent
```

### Step 4: Seed standards knowledge base

```powershell
python -m agents.ingest_agent
```

### Step 5: Run Streamlit UI

```powershell
streamlit run ui/streamlit_app.py
```

Open:

```text
http://localhost:8501
```

---

## 7. Demo Flow

1. Open Streamlit UI.
2. Click **Seed / Refresh Standards KB**.
3. Go to **RFC Review Demo**.
4. Use the sample RFC or paste a new RFC.
5. Click **Run Review**.
6. Review:

   * Retrieval status.
   * Retrieved standards count.
   * Rubric score.
   * Final decision.
   * Review report.
7. Go to **RAG Evidence** to see the retrieved standards.
8. Go to **Architecture View** to explain the system flow.

---

## 8. Example Output

For the sample Customer Notification Service RFC, ArchReviewAI may generate a result like:

```text
Rubric Score: 3/10

Final Decision: ARCHITECT_REVIEW

Reason:
The RFC has significant gaps in security, reliability, observability, rollback, and operations. It requires human architect review before approval.
```

Example findings:

* Authentication and authorization are not clearly defined.
* PII handling for customer phone numbers is incomplete.
* SMS provider secret handling is vague.
* Scalability lacks RPS, peak load, and SLOs.
* Reliability lacks timeout, DLQ, idempotency, and disaster recovery.
* Observability lacks metrics, traces, alert thresholds, dashboards, and runbooks.
* Rollback strategy does not define owner, time, or data rollback.
* Cost and support ownership are missing.

---

## 9. Architecture Principles

ArchReviewAI follows these principles:

* Do not rely only on generic LLM memory.
* Retrieve relevant enterprise standards before review.
* Keep scoring deterministic and auditable.
* Use the LLM for explanation, not uncontrolled decisioning.
* Keep human architects in the loop for high-risk cases.
* Make review evidence visible.
* Separate MVP from production roadmap.

---

## 10. What This Project Demonstrates

This project demonstrates practical GenAI architecture concepts:

* RAG over enterprise standards.
* Chunking and embeddings.
* Vector database retrieval.
* Prompt engineering.
* LLM orchestration.
* Deterministic scoring.
* Human-in-the-loop decisioning.
* Streamlit UI integration.
* Prototype-to-production thinking.
* Enterprise AI governance mindset.

---

## 11. Roadmap

### Phase 1 — MVP Foundation

Status: Mostly implemented.

* Create project scaffold.
* Create enterprise standards docs.
* Implement ingestion.
* Implement chunking.
* Generate embeddings.
* Store standards in ChromaDB.
* Retrieve relevant standards.
* Build prompt templates.
* Generate RFC review report.
* Build Streamlit UI.
* Add deterministic rubric scoring.

---

### Phase 2 — Retrieval Quality Improvements

Planned:

* Add hybrid search using keyword + vector retrieval.
* Add reranking for better context selection.
* Improve query expansion.
* Add category-wise retrieval:

  * RFC template.
  * Security.
  * Scalability.
  * Reliability.
  * Observability.
  * Cost and operations.
* Add deduplication for repeated chunks.
* Add metadata filters.
* Add retrieval evaluation.

Metrics to add:

* Recall@K.
* Precision@K.
* MRR.
* Context relevance.
* Retrieval diversity.

---

### Phase 3 — Multi-Agent Review

Planned / partially started:

* Add specialist agents:

  * Security Review Agent.
  * Scalability and Reliability Agent.
  * Observability Agent.
  * Cost and Operations Agent.
* Add supervisor agent.
* Merge specialist findings into a single final recommendation.
* Resolve conflicting agent outputs.
* Add agent-level scoring.
* Add human-review escalation rules.

Target pattern:

```text
RFC
 ↓
Retriever
 ↓
Specialist Agents
 ↓
Supervisor
 ↓
Final Decision
```

---

### Phase 4 — Evaluation and Observability

Planned:

* Add LangSmith tracing.
* Track retrieved context.
* Track prompts and model responses.
* Add RAGAS evaluation.
* Evaluate faithfulness.
* Evaluate answer relevancy.
* Evaluate context precision.
* Evaluate context recall.
* Add regression tests for golden RFC examples.
* Track latency and token usage.

---

### Phase 5 — Production Hardening

Planned:

* Add FastAPI backend.
* Add Docker deployment.
* Add CI/CD pipeline.
* Add authentication and RBAC.
* Add audit logging.
* Add prompt versioning.
* Add policy versioning.
* Add secure secrets handling.
* Add rate limiting.
* Add request validation.
* Add PII redaction.
* Add approval workflow.

---

### Phase 6 — Enterprise Integrations

Planned:

* Integrate with Confluence or SharePoint for standards.
* Integrate with GitHub or GitLab for design documents.
* Add Jira ticket creation for revision requests.
* Add Slack or Teams notifications.
* Add enterprise policy repository sync.
* Add review history and dashboard.
* Add architect approval workflow.

---

### Phase 7 — Advanced Agentic AI Extensions

Future:

* LangGraph workflow orchestration.
* MCP-style tool integration.
* Graph RAG over architecture dependencies.
* Multi-document RFC review.
* Architecture diagram review.
* ADR generation.
* Risk register generation.
* Automated review comments.
* Enterprise architecture governance dashboard.

---

## 12. Known Limitations

Current limitations:

* Scoring is keyword/signal-based and should be improved with richer policy rules.
* Retrieval currently depends on local ChromaDB.
* Evaluation metrics are planned but not fully implemented.
* Specialist agents are planned/partially started.
* Production authentication and access control are not yet implemented.
* This is a portfolio MVP, not a production deployment.
