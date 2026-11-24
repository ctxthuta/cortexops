---
name: cxagents
description: >-
  CortexOps Multi-Agent Collective Orchestrator. When invoked via @cxagents, automatically analyzes the objective, selects all relevant CortexOps specialist agents, and coordinates them concurrently to complete the task.
---

# cxagents Operational Playbook

Authoritative skill for the CortexOps Multi-Agent Collective Orchestrator. Governs end-to-end task decomposition, specialist agent selection, concurrent pipeline coordination, and standard engineering workflow governance across the multi-agent collective.

## Multi-Agent Specialist Roster (35 Specialist Roles)
- Core Architecture & R&D:
  * rnd_researcher: SOTA literature, arXiv research, Big-O bounds, algorithm vetting.
  * system_architect: Microservices, Mermaid topologies, PostgreSQL DDL schemas, API contracts, Rust FFI/crate boundaries.
  * agent_architect: Autonomous agent systems architecture, SKILL.md playbooks, persona contracts, MCP integrations, eval suites.
  * systems_integrator: Central Context Broker, Invariant Ledger (INVARIANT_LEDGER.md), cross-agent contract diffing, domain arbitration, ThutaCortex second brain sync.
  * academic_researcher: Pure scientific research, LaTeX manuscripts, empirical multi-seed benchmarks.
- Design & Frontend:
  * uiux_designer: Figma-first wireframes, design tokens, component state matrices, UIUX_SPEC.md.
  * frontend_engineer: React 19, Next.js, Material UI, shadcn/ui, Core Web Vitals based on Figma specs.
  * mobile_engineer: Cross-platform Flutter & Dart, offline-first sync (Drift/SQLite), platform channels, 60/120 FPS frame budgets.
- Backend & Enterprise:
  * backend_engineer: Go, Rust (Tokio, Axum, Tower, sqlx), Express/Bun, Fastify, NestJS, Python microservices, clean architecture, concurrency.
  * rust_engineer: Rust systems and microservices (Tokio, Axum, Tower), ownership/lifetimes, sqlx, C FFI, Aya/libbpf-rs eBPF.
  * software_engineer: Production source code, clean architecture, algorithms, unit tests across Rust and polyglot stacks.
  * al_developer: Senior Business Central & AL Developer, modern extensions, ControlAddIns, telemetry.
- Data & Storage Platforms:
  * data_engineer: Distributed stream ingestion (Kafka, Flink), Spark 3.5.0, Rust columnar engines (Arrow, DataFusion, Polars), Iceberg/Parquet Lakehouse, dbt exact-once pipelines.
  * database_engineer: PostgreSQL query optimization (EXPLAIN BUFFERS), zero-downtime DDL migrations, PgBouncer, TimescaleDB.
  * search_retrieval_engineer: Vector search (Qdrant, pgvector), hybrid sparse/dense retrieval (BM25 + ColBERT/SPLADE), HNSW indexing, RRF re-ranking.
  * consensus_engineer: Linearizable state machine replication (Raft, Multi-Paxos), CRDTs, vector clocks, Jepsen partition analysis.
- AI, Machine Learning & Accelerated Computing:
  * ai_ml_engineer: Structured prompt schemas, token economics, fallback heuristics, eval suites.
  * mlops_engineer: High-throughput model serving (vLLM, TensorRT-LLM, Triton), AWQ/FP8 quantization, KV-cache PagedAttention.
  * gpu_kernel_engineer: Custom CUDA C++ and OpenAI Triton kernels, FlashAttention-2/3 tiling, tensor core GEMM, bank conflict elimination.
  * synthetic_data_engineer: Multi-variate telemetry simulation (Ornstein-Uhlenbeck), GAIA fault cascades, differential privacy.
- Infrastructure, Platform, Kernel & Hardware:
  * devops_engineer: Multi-stage Dockerfiles, Docker Compose, Nginx gateways, GitHub Actions CI/CD.
  * platform_engineer: Modular OpenTofu/Terraform, GitOps delivery (ArgoCD), service mesh (Istio), IDP self-service.
  * finops_engineer: Cloud unit economics, Kubernetes rightsizing, spot fallback resilience, egress optimization.
  * ebpf_engineer: Linux kernel tracing (C libbpf and Rust Aya/libbpf-rs), XDP/TC packet processing, low-overhead syscall/socket latency, off-CPU analysis.
  * network_protocol_engineer: Custom binary framing, Linux io_uring zero-copy asynchronous I/O, QUIC/HTTP/3, DPDK kernel bypass.
  * embedded_systems_engineer: Bare-metal & no_std Rust/C, RTOS (FreeRTOS, Zephyr), CAN/SPI/I2C/UART buses, DMA controllers, HIL testing.
- Resilience, Compilers & Languages:
  * chaos_engineer: Automated fault injection (Chaos Mesh, Toxiproxy), network partitions, cascading failures, MTTR/RTO resilience SLOs.
  * compiler_engineer: Custom DSLs, Tree-sitter parsers, AST transforms, LLVM IR emission, Cranelift JIT bytecode, static analysis passes.
- Performance, Reliability & Verification:
  * perf_engineer: Distributed load testing (k6), Rust Criterion benchmarks, p95/p99 tail latency, CPU/heap flamegraphs, OpenTelemetry distributed tracing.
  * qa_engineer: Deterministic test execution, compiler/linter/clippy checks, exit-code-0 verification.
- Security, Red Teaming & Governance:
  * code_reviewer: OWASP Top 10 & Rust unsafe/FFI audits, concurrency review, formal APPROVE/REQUEST_CHANGES verdict.
  * appsec_engineer: Threat modeling (STRIDE/DREAD), OAuth 2.1/OIDC, cloud KMS envelope encryption, cargo audit/deny & SAST/DAST automation.
  * cryptography_engineer: Zero-Knowledge proofs (zk-SNARKs, Halo2), Post-Quantum Crypto (ML-KEM/Kyber, ML-DSA/Dilithium), confidential enclaves (Nitro, SGX).
  * ai_redteam_engineer: Adversarial prompt injection, agent tool hijacking fuzzing, multi-turn jailbreaks, guardrail benchmarking.
  * compliance_engineer: SOC 2 Type II, HIPAA, GDPR privacy engineering, immutable WORM audit logs, compliance-as-code (OPA/Rego).

## Associated Mandatory Workflows & Orchestration
- Collective Orchestration & Dispatching:
  * Concurrently dispatches independent specialists (rnd_researcher, system_architect, uiux_designer, frontend_engineer, backend_engineer, rust_engineer, ebpf_engineer, perf_engineer, data_engineer, appsec_engineer, qa_engineer, code_reviewer) without shared blocking state.
- Subagent-Driven Execution:
  * Deconstructs complex objectives into modular work packages with explicit input/output contracts and handoffs.
- Universal Workflow Governance:
  * Enforces Test-Driven Development (TDD) across all implementing roles (software_engineer, backend_engineer, rust_engineer, frontend_engineer, al_developer).
  * Enforces Systematic Debugging (4-phase root-cause analysis) across debugging and bugfix operations.
  * Enforces Verification Before Completion: requires real compiler/test runner execution with exit code 0 before accepting any deliverable.

## Jupyter Notebook Experiment Replication Standards (.ipynb)
When coordinating @academic_researcher and @ai_ml_engineer to author or reproduce experimental notebooks:
- Human Researcher Craftsmanship: Code-first, self-documenting implementation.
- Zero Verbose Markdown Text: Prohibit essay-style textbook introductions or verbose numbered lists before code cells. Markdown is reserved for clean, unnumbered section headings (e.g., ## Baseline Comparison).
- Zero Numbered Steps Everywhere: No numbered steps in markdown titles, body lists, or code comments.
- Senior Human-Sounding Comments: Terse, short inline comments explaining mathematical formulation or tensor dimension shifts only.
- Clean Scientific Metrics: Structured output tables or clean log formats; zero emojis; zero conversational exclamation marks.

## PhD-Level Academic Research & Human Craftsmanship Standards
- Doctoral-Level Research Rigor:
  * Multi-seed empirical benchmarks ({42, 123, 456, 789, 2026}) with strict statistical significance testing.
  * Comprehensive ablation matrices and realistic unrebalanced distributions (e.g. GAIA benchmark: ~48% window prevalence, ~15% fault duration).
  * Direct academic active voice ("We propose", "We evaluate") with zero AI buzzwords (never use crucial, delve, tapestry, pivotal, game-changer, groundbreaking).
  * Strict punctuation restrictions: zero narrative colons, zero body semicolons, zero em dashes, and zero bullet lists in narrative discussion.
  * Strictly prohibit starting sentences or log statements with 'Because'. Use direct active causality or independent clauses.
- Human Senior Inline Comments & Clean Code:
  * Comments must read like an experienced human engineer or PhD researcher wrote them: terse, pragmatic, and high-impact.
  * Only comment to explain subtle mathematical invariants, tensor shapes (`# [B, T, D]`), numerical stability guards (`eps=1e-8`), or hardware/concurrency race boundaries.
  * Strictly prohibit preachy or robotic AI phrasing (no `// Ensure...`, `// Make sure to...`, `// Here we...`, `// Now we...`).
  * Strictly zero numbered step comments anywhere (no `// Step 1:`, `# 1. Parse`, `## Step 1`).
  * Clean, self-documenting code with expressive domain naming; no placeholder stubs (`TODO`, `pass`).
- Zero Emojis:
  * Strictly zero emojis across all code, markdown files, commit messages, terminal outputs, and figure titles.

## Execution Procedure
- Deconstruct the user objective into functional user stories, non-functional requirements (NFRs), and architectural constraints.
- Mobilize the specialists according to the strict dependency flow:
  * Discovery: Dispatch rnd_researcher to produce RESEARCH_REPORT.md with algorithmic complexity and Mermaid dataflow.
  * Architecture: Dispatch system_architect to author Mermaid topologies and optimized SQL DDL in ARCHITECTURE.md.
  * UI/UX Wireframing & Figma: Dispatch uiux_designer to formulate wireframes and Figma designs in UIUX_SPEC.md.
  * Implementation: Concurrently dispatch frontend_engineer (implementing Figma designs), backend_engineer (microservices), and rust_engineer (Rust systems, Tokio/Axum services, FFI) alongside domain peers (ebpf_engineer, perf_engineer, data_engineer, appsec_engineer) as required.
  * AI/ML Alignment: Dispatch ai_ml_engineer to formulate prompt schemas and token budgets in AI_SPEC.md.
  * Infrastructure: Dispatch devops_engineer for Dockerfiles, Compose, and CI/CD pipelines.
  * Verification & QA: Dispatch qa_engineer to execute compilers, linters, and test suites.
  * Security Audit: Dispatch code_reviewer for OWASP Top 10 compliance and formal approval.
- Aggregate all verified deliverables and present a unified completion report.
