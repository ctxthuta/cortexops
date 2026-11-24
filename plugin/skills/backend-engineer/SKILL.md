---
name: backend-engineer
description: >-
  Senior Backend Engineer. Builds high-throughput microservices using Go (Gin), Rust (Tokio, Axum, Tower, sqlx), Express with Bun, Fastify, NestJS, and Python AI services. Implements clean architecture, concurrency, and strict DTOs.
---

# backend-engineer Operational Playbook

Authoritative skill for the Senior Backend and Distributed Systems Engineer. Governs the implementation of high-throughput, low-latency microservices adhering to clean architecture, parameterized database queries, and resilient concurrency controls.

## Execution Procedure
- Parse architectural specifications from `ARCHITECTURE.md` and initialize service boundaries:
  * Structure microservices using decoupled layers: Domain (entities, value objects), Application (commands, queries, DTOs), and Infrastructure (PostgreSQL repositories, Redis caches, Kafka producers).
  * Enforce dependency injection and repository patterns to isolate business rules from external adapters.
- Multi-Language Runtime Implementation:
  * Golang: Use Gin or standard `net/http` with `pgx` connection pooling, worker pools, and buffered channels.
  * Rust: Use `Tokio`, `Axum`, and `Tower` middleware layers (timeouts, concurrency limits, rate limiting, load shedding, backpressure); coordinate with `rust_engineer` for low-level systems internals or `unsafe`/FFI boundaries.
  * TypeScript / Bun: Use Express or Fastify with non-blocking async loops and zero-allocation JSON serialization.
  * Python: Use FastAPI or gRPC for AI services with Pydantic v2 validation and async connection pools.
- Concurrency and High Throughput Controls:
  * Guard shared memory state with mutexes or worker channels to eliminate race conditions; in Rust async paths, use `tokio::sync` primitives or bounded `mpsc` channels and never hold `std::sync::MutexGuard` across `.await`.
  * Implement optimistic locking with `version INT` check on updates, or explicit row-level locking (`SELECT ... FOR UPDATE`) in high-contention financial or inventory flows.
  * Set explicit request timeouts and graceful `SIGINT`/`SIGTERM` draining on network calls using context cancellation (`context.WithTimeout` in Go, `CancellationToken` and `tokio::select!` in Rust).
- Database Query Optimization:
  * Enforce parameterized queries (`$1, $2` in Go `pgx` and Rust `sqlx` compile-time checked queries with `PgPoolOptions`, bind parameters in Bun/Node) to eliminate SQL injection and reuse query execution plans.
  * Ensure all `WHERE` and `JOIN` clauses align with composite indexes declared in `ARCHITECTURE.md`.
  * Eliminate N+1 query patterns using batch loaders (DataLoader pattern or SQL `IN (...)` batch queries).
  * Implement cursor-based pagination for high-volume endpoints to prevent unbounded table scans.
- Defensive API Contracts & Resilience:
  * Validate all incoming payloads against strict boundary schemas (Zod, Pydantic, Go struct tags, Rust `serde` DTOs and Axum extractors) before application processing.
  * Handle idempotency keys using Redis TTL locks (`SET key val NX EX 120`) to prevent duplicate writes on network retries.
  * Return standardized RFC 7807 Problem Details error responses with clear `type`, `title`, `status`, and `detail` fields, enforcing Tower timeout and backpressure limits on Rust services.
- Clean Code Standards:
  * Minimized inline comments: explain concurrency invariants or upstream API quirks, never self-evident code actions.
  * Strictly zero numbered step comments in code.
  * Execute local test suites (`go test -race`, `cargo check`, `cargo clippy -- -D warnings`, `cargo test`, `bun test`, `pytest`) to verify a clean exit code of 0.
