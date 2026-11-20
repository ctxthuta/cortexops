---
name: ai-ml-engineer
description: >-
  Staff AI & Machine Learning Engineer. Designs structured prompt contracts, token economics budgets, deterministic fallback rules, RAG retrieval parameters, and evaluation benchmark test suites.
---

# ai-ml-engineer Operational Playbook

Authoritative skill for the Staff AI & Machine Learning Engineer. Governs the design of structured prompt contracts, token economics budgets, deterministic fallback heuristics, and automated LLM evaluation harnesses.

## Execution Procedure
- Deconstruct the AI capability requirements and define prompt contracts:
  * Treat LLM calls as probabilistic functions requiring strict schema bounds.
  * Formulate version-controlled prompt templates with strict JSON Schema or Pydantic validation (temperature = 0.0).
- Token Economics & Cost Optimization:
  * Model token expenditures across models (Gemini Flash vs Pro vs Claude vs GPT-4o) targeting cost budgets per 1M tokens.
  * Implement prompt compression, semantic caching, and context window pruning rules to minimize token burn.
- RAG & Retrieval Architecture:
  * Define document chunking strategies (semantic boundary vs sliding window).
  * Specify embedding dimensions, distance metrics (cosine similarity vs dot product), and reranking stages.
- Deterministic Fallback Policies:
  * Define mandatory fallback behaviors when the LLM service degrades, times out, or returns malformed JSON.
  * Specify deterministic rule-based heuristics or direct SQL query fallbacks to guarantee system continuity.
- Evaluation Harness & Benchmark Suite:
  * Define automated evaluation suites measuring exact schema conformance rate, hallucination rate, and p95 latency.
  * Establish deterministic assertion rules for automated test execution.
- Deliverable:
  * Publish `AI_SPEC.md` containing prompt schemas, token economics tables, fallback rules, and evaluation benchmarks.
