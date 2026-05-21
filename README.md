# ArchReviewAI — Agentic RAG Copilot for Enterprise RFC Reviews

## 1. Problem

Engineering teams write RFCs, design documents, and architecture proposals before building important systems. These documents often wait for senior architect review.

Common problems:
- Senior architects become review bottlenecks.
- RFC quality varies across teams.
- Security, scalability, reliability, observability, and cost gaps are missed.
- Review feedback is inconsistent.
- Projects get delayed because issues are found late.

## 2. Target Users

- Software engineers writing RFCs.
- Tech leads reviewing team proposals.
- Enterprise architects and solution architects.
- Platform engineering teams.
- Security and reliability reviewers.

## 3. Business Value

ArchReviewAI provides a first-pass architecture review before senior architect approval.

Expected value:
- Reduce first-pass RFC review time from days to minutes.
- Improve consistency of architecture review feedback.
- Enforce enterprise standards early.
- Identify missing non-functional requirements.
- Create an auditable review trail.
- Free senior architects for high-risk and strategic reviews.

## 4. Core Use Case

An engineer submits an RFC or design document.

ArchReviewAI:
1. Reads the RFC.
2. Retrieves relevant enterprise architecture standards using RAG.
3. Runs specialist reviews for security, scalability, and observability.
4. Produces a structured review report.
5. Gives a final recommendation:
   - APPROVE
   - NEEDS_REVISION
   - ARCHITECT_REVIEW
6. Shows evidence from the retrieved standards.

## 5. Decision Boundary

ArchReviewAI does not replace senior architects.

The AI performs first-pass review and recommendation.

Final approval remains with human architects for:
- High-risk designs.
- Security-sensitive systems.
- Production architecture decisions.
- Ambiguous or insufficient context cases.

## 6. MVP Scope

The MVP includes:
- Streamlit UI for interactive demo.
- RFC paste/upload.
- Enterprise standards knowledge base.
- Chunking and embeddings.
- ChromaDB vector store.
- LangChain-based RAG retrieval.
- Gemini-based review generation.
- Specialist agents:
  - Security reviewer.
  - Scalability reviewer.
  - Observability reviewer.
- Supervisor recommendation.
- LangSmith observability.
- RAGAS evaluation.
- Retrieval metrics such as Recall@K, Precision@K, and MRR.

## 7. Out of MVP

These are Day 3 or later extensions:
- n8n workflow automation.
- MCP tool integration.
- Graph RAG.
- FastAPI backend.
- Docker deployment.
- GitHub Actions CI/CD.
- Slack/Jira/Confluence integration.
- Multimodal architecture diagram review.

## 8. Architecture Principles

- Use RAG to ground reviews in enterprise standards.
- Use specialist agents for focused review dimensions.
- Use supervisor logic for final recommendation.
- Use LangSmith for traceability and debugging.
- Use RAGAS and retrieval metrics for quality evaluation.
- Keep human architects in the approval loop.
- Keep MVP demo-first and minimal-code.

## 9. Success Metrics

Technical metrics:
- Recall@K for standards retrieval.
- Precision@K for context quality.
- MRR for ranking quality.
- RAGAS faithfulness.
- RAGAS answer relevancy.
- RAGAS context precision.
- RAGAS context recall.

Business metrics:
- First-pass review time reduction.
- Number of missing RFC sections detected.
- Reduction in repeated architecture review comments.
- Architect override rate.
- RFC author satisfaction.

## 10. One-Line Pitch

ArchReviewAI reduces architecture review bottlenecks by using Agentic RAG to review RFCs against enterprise standards before senior architect approval.