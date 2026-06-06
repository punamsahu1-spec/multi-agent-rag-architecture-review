# ArchReviewAI Demo Runbook

## Purpose

This runbook explains how to run ArchReviewAI for a customer or interview demo.

ArchReviewAI is an Agentic RAG copilot for enterprise RFC/design-document reviews. It reviews RFCs against architecture standards, retrieves evidence, applies deterministic scoring, runs specialist reviews, makes a supervisor recommendation, and routes risky RFCs to human review.

---

## Demo Modes

### Demo Mode

Use this when you do not want to depend on any external LLM.

```env
DEMO_MODE=true